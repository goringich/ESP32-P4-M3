#include "app_stepper.h"

#include <inttypes.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>

#include "driver/gpio.h"
#include "driver/uart.h"
#include "esp_log.h"
#include "sdkconfig.h"

#define APP_STEPPER_COLOR_RESET "\x1b[0m"
#define APP_STEPPER_COLOR_HDR "\x1b[38;5;214m"
#define APP_STEPPER_COLOR_CMD "\x1b[38;5;45m"
#define APP_STEPPER_COLOR_OK "\x1b[38;5;82m"
#define APP_STEPPER_COLOR_WARN "\x1b[38;5;220m"

#define APP_STEPPER_UART_PORT UART_NUM_0
#define APP_STEPPER_UART_RX_BUF_SIZE 256
#define APP_STEPPER_UART_TX_BUF_SIZE 0

#define APP_STEPPER_SWEEP_STEPS 200U
#define APP_STEPPER_EDGE_PAUSE_MS 500U
#define APP_STEPPER_DUPLICATE_CMD_GUARD_MS 150U
#define APP_STEPPER_MIN_DELAY_MS 20U
#define APP_STEPPER_MAX_DELAY_MS 5000U

static const char *TAG = "app_stepper";

typedef struct {
  uint8_t in1;
  uint8_t in2;
  uint8_t in3;
  uint8_t in4;
  const char *label;
} app_stepper_phase_t;

typedef enum {
  APP_STEPPER_MODE_STOP = 0,
  APP_STEPPER_MODE_FORWARD,
  APP_STEPPER_MODE_REVERSE,
  APP_STEPPER_MODE_SWEEP,
} app_stepper_mode_t;

typedef enum {
  APP_STEPPER_SWEEP_FORWARD = 0,
  APP_STEPPER_SWEEP_REVERSE,
  APP_STEPPER_SWEEP_PAUSE_AFTER_FORWARD,
  APP_STEPPER_SWEEP_PAUSE_AFTER_REVERSE,
} app_stepper_sweep_state_t;

typedef struct {
  app_stepper_mode_t mode;
  app_stepper_sweep_state_t sweep_state;
  size_t phase_index;
  uint32_t step_delay_ms;
  uint32_t last_step_ms;
  uint32_t pause_started_ms;
  uint32_t moved_steps_in_leg;
  uint32_t total_steps;
  bool coils_enabled;
  bool uart_ready;
  bool led_state;
  uint8_t last_cmd;
  uint32_t last_cmd_ms;
  uint32_t last_telemetry_ms;
} app_stepper_state_t;

static void app_stepper_log_block(const char *title);
static const char *app_stepper_mode_to_str(app_stepper_mode_t mode);
static uint32_t app_stepper_delay_adjust_delta_ms(uint32_t current_delay_ms);
static float app_stepper_steps_per_second(uint32_t delay_ms);
static void app_stepper_log_timing(const char *reason);
static void app_stepper_print_help(void);
static void app_stepper_print_status(void);
static const char *app_stepper_sweep_state_to_str(app_stepper_sweep_state_t state);
static const char *app_stepper_cmd_to_str(uint8_t cmd);
static void app_stepper_emit_telemetry(const char *reason);

static esp_err_t app_stepper_gpio_init(void);
static esp_err_t app_stepper_uart_init(void);
static void app_stepper_led_init(void);
static void app_stepper_led_toggle(void);
static void app_stepper_led_set(bool on);

static void app_stepper_apply_phase(const app_stepper_phase_t *phase);
static void app_stepper_release(void);
static void app_stepper_step_forward_once(void);
static void app_stepper_step_reverse_once(void);
static void app_stepper_set_mode(app_stepper_mode_t mode);
static void app_stepper_handle_uart(void);
static void app_stepper_handle_command(uint8_t cmd);
static void app_stepper_apply_named_phase(size_t phase_index);

static const app_stepper_phase_t s_phases[] = {
  {1, 0, 1, 0, "phase A"},
  {0, 1, 1, 0, "phase B"},
  {0, 1, 0, 1, "phase C"},
  {1, 0, 0, 1, "phase D"},
};

static app_stepper_state_t s_stepper = {
  .mode = APP_STEPPER_MODE_STOP,
  .sweep_state = APP_STEPPER_SWEEP_FORWARD,
  .phase_index = 0,
  .step_delay_ms = CONFIG_APP_L293D_STEP_DELAY_MS,
  .last_step_ms = 0,
  .pause_started_ms = 0,
  .moved_steps_in_leg = 0,
  .total_steps = 0,
  .coils_enabled = false,
  .uart_ready = false,
  .led_state = false,
  .last_cmd = 0,
  .last_cmd_ms = 0,
  .last_telemetry_ms = 0,
};

static void app_stepper_log_block(const char *title) {
  static const char divider[] = "----------------------------------------";

  ESP_LOGI(TAG, "%s%s%s", APP_STEPPER_COLOR_HDR, divider, APP_STEPPER_COLOR_RESET);
  if (title != NULL && title[0] != '\0') {
    ESP_LOGI(TAG, "%s  %s  %s", APP_STEPPER_COLOR_HDR, title, APP_STEPPER_COLOR_RESET);
  }
  ESP_LOGI(TAG, "%s%s%s", APP_STEPPER_COLOR_HDR, divider, APP_STEPPER_COLOR_RESET);
}

static const char *app_stepper_mode_to_str(app_stepper_mode_t mode) {
  switch (mode) {
    case APP_STEPPER_MODE_STOP:
      return "stop";
    case APP_STEPPER_MODE_FORWARD:
      return "forward";
    case APP_STEPPER_MODE_REVERSE:
      return "reverse";
    case APP_STEPPER_MODE_SWEEP:
      return "sweep";
    default:
      return "unknown";
  }
}

static uint32_t app_stepper_delay_adjust_delta_ms(uint32_t current_delay_ms) {
  if (current_delay_ms >= 1000U) {
    return 200U;
  }
  if (current_delay_ms >= 500U) {
    return 100U;
  }
  if (current_delay_ms >= 250U) {
    return 50U;
  }
  if (current_delay_ms >= 100U) {
    return 20U;
  }
  return 10U;
}

static float app_stepper_steps_per_second(uint32_t delay_ms) {
  if (delay_ms == 0U) {
    return 0.0f;
  }
  return 1000.0f / (float)delay_ms;
}

static const char *app_stepper_sweep_state_to_str(app_stepper_sweep_state_t state) {
  switch (state) {
    case APP_STEPPER_SWEEP_FORWARD:
      return "forward";
    case APP_STEPPER_SWEEP_REVERSE:
      return "reverse";
    case APP_STEPPER_SWEEP_PAUSE_AFTER_FORWARD:
      return "pause_after_forward";
    case APP_STEPPER_SWEEP_PAUSE_AFTER_REVERSE:
      return "pause_after_reverse";
    default:
      return "unknown";
  }
}

static const char *app_stepper_cmd_to_str(uint8_t cmd) {
  switch (cmd) {
    case 0:
      return "";
    case '\r':
      return "\\r";
    case '\n':
      return "\\n";
    default: {
      static char buf[2];
      buf[0] = (char)cmd;
      buf[1] = '\0';
      return buf;
    }
  }
}

static void app_stepper_emit_telemetry(const char *reason) {
  printf("@telemetry {\"kind\":\"stepper\",\"reason\":\"%s\",\"mode\":\"%s\","
         "\"sweep_state\":\"%s\",\"step_delay_ms\":%" PRIu32 ",\"steps_per_second\":%.2f,"
         "\"phase_index\":%u,\"total_steps\":%" PRIu32 ",\"coils_enabled\":%s,"
         "\"sweep_steps\":%" PRIu32 ",\"uart_ready\":%s,\"last_command\":\"%s\","
         "\"pins\":{\"in1\":%d,\"in2\":%d,\"in3\":%d,\"in4\":%d},\"led_gpio\":%d}\n",
         reason != NULL ? reason : "update",
         app_stepper_mode_to_str(s_stepper.mode),
         app_stepper_sweep_state_to_str(s_stepper.sweep_state),
         s_stepper.step_delay_ms,
         (double)app_stepper_steps_per_second(s_stepper.step_delay_ms),
         (unsigned)s_stepper.phase_index,
         s_stepper.total_steps,
         s_stepper.coils_enabled ? "true" : "false",
         s_stepper.moved_steps_in_leg,
         s_stepper.uart_ready ? "true" : "false",
         app_stepper_cmd_to_str(s_stepper.last_cmd),
         CONFIG_APP_L293D_IN1_GPIO,
         CONFIG_APP_L293D_IN2_GPIO,
         CONFIG_APP_L293D_IN3_GPIO,
         CONFIG_APP_L293D_IN4_GPIO,
#if CONFIG_APP_STEPPER_LED_ENABLE
         CONFIG_APP_STEPPER_LED_GPIO
#else
         -1
#endif
  );
}

static void app_stepper_log_timing(const char *reason) {
  ESP_LOGI(TAG,
           "%s delay=%" PRIu32 " ms (%.2f steps/s)%s",
           reason != NULL ? reason : "timing",
           s_stepper.step_delay_ms,
           app_stepper_steps_per_second(s_stepper.step_delay_ms),
           APP_STEPPER_COLOR_RESET);
  app_stepper_emit_telemetry(reason);
}

static void app_stepper_print_help(void) {
  ESP_LOGI(TAG, "%scommands%s", APP_STEPPER_COLOR_CMD, APP_STEPPER_COLOR_RESET);
  ESP_LOGI(TAG, "  h : print help");
  ESP_LOGI(TAG, "  p : print status");
  ESP_LOGI(TAG, "  s : stop");
  ESP_LOGI(TAG, "  f : run forward");
  ESP_LOGI(TAG, "  r : run reverse");
  ESP_LOGI(TAG, "  w : sweep forward/reverse");
  ESP_LOGI(TAG, "  1 : single step forward");
  ESP_LOGI(TAG, "  2 : single step reverse");
  ESP_LOGI(TAG, "  a : hold phase A");
  ESP_LOGI(TAG, "  b : hold phase B");
  ESP_LOGI(TAG, "  c : hold phase C");
  ESP_LOGI(TAG, "  d : hold phase D");
  ESP_LOGI(TAG, "  +/= : speed up (adaptive delay decrease)");
  ESP_LOGI(TAG, "  -/_ : slow down (adaptive delay increase)");
  ESP_LOGI(TAG, "  z : release coils");
}

static void app_stepper_print_status(void) {
  ESP_LOGI(TAG,
           "status: mode=%s delay=%" PRIu32 " ms (%.2f steps/s) phase=%u total_steps=%" PRIu32
           " coils=%s sweep_steps=%" PRIu32 " uart=%s",
           app_stepper_mode_to_str(s_stepper.mode),
           s_stepper.step_delay_ms,
           app_stepper_steps_per_second(s_stepper.step_delay_ms),
           (unsigned)s_stepper.phase_index,
           s_stepper.total_steps,
           s_stepper.coils_enabled ? "on" : "off",
           s_stepper.moved_steps_in_leg,
           s_stepper.uart_ready ? "ready" : "off");
  app_stepper_emit_telemetry("status");
}

static esp_err_t app_stepper_gpio_init(void) {
  gpio_config_t cfg = {
    .pin_bit_mask = (1ULL << CONFIG_APP_L293D_IN1_GPIO) |
                    (1ULL << CONFIG_APP_L293D_IN2_GPIO) |
                    (1ULL << CONFIG_APP_L293D_IN3_GPIO) |
                    (1ULL << CONFIG_APP_L293D_IN4_GPIO),
    .mode = GPIO_MODE_OUTPUT,
    .pull_up_en = GPIO_PULLUP_DISABLE,
    .pull_down_en = GPIO_PULLDOWN_DISABLE,
    .intr_type = GPIO_INTR_DISABLE,
  };

  return gpio_config(&cfg);
}

static void app_stepper_led_init(void) {
#if CONFIG_APP_STEPPER_LED_ENABLE
  gpio_config_t cfg = {
    .pin_bit_mask = (1ULL << CONFIG_APP_STEPPER_LED_GPIO),
    .mode = GPIO_MODE_OUTPUT,
    .pull_up_en = GPIO_PULLUP_DISABLE,
    .pull_down_en = GPIO_PULLDOWN_DISABLE,
    .intr_type = GPIO_INTR_DISABLE,
  };

  ESP_ERROR_CHECK(gpio_config(&cfg));
  gpio_set_level((gpio_num_t)CONFIG_APP_STEPPER_LED_GPIO, 0);
#endif
}

static void app_stepper_led_set(bool on) {
#if CONFIG_APP_STEPPER_LED_ENABLE
  gpio_set_level((gpio_num_t)CONFIG_APP_STEPPER_LED_GPIO, on ? 1 : 0);
#else
  (void)on;
#endif
}

static void app_stepper_led_toggle(void) {
#if CONFIG_APP_STEPPER_LED_ENABLE
  s_stepper.led_state = !s_stepper.led_state;
  gpio_set_level((gpio_num_t)CONFIG_APP_STEPPER_LED_GPIO, s_stepper.led_state ? 1 : 0);
#endif
}

static esp_err_t app_stepper_uart_init(void) {
  const uart_config_t uart_cfg = {
    .baud_rate = CONFIG_APP_STEPPER_UART_BAUD_RATE,
    .data_bits = UART_DATA_8_BITS,
    .parity = UART_PARITY_DISABLE,
    .stop_bits = UART_STOP_BITS_1,
    .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
    .source_clk = UART_SCLK_DEFAULT,
  };

  esp_err_t err = uart_driver_install(
    APP_STEPPER_UART_PORT,
    APP_STEPPER_UART_RX_BUF_SIZE,
    APP_STEPPER_UART_TX_BUF_SIZE,
    0,
    NULL,
    0
  );

  if (err != ESP_OK && err != ESP_ERR_INVALID_STATE) {
    ESP_LOGE(TAG, "uart_driver_install failed: %s", esp_err_to_name(err));
    return err;
  }

  err = uart_param_config(APP_STEPPER_UART_PORT, &uart_cfg);
  if (err != ESP_OK) {
    ESP_LOGE(TAG, "uart_param_config failed: %s", esp_err_to_name(err));
    return err;
  }

  err = uart_set_mode(APP_STEPPER_UART_PORT, UART_MODE_UART);
  if (err != ESP_OK) {
    ESP_LOGE(TAG, "uart_set_mode failed: %s", esp_err_to_name(err));
    return err;
  }

  s_stepper.uart_ready = true;
  return ESP_OK;
}

static void app_stepper_apply_phase(const app_stepper_phase_t *phase) {
  gpio_set_level((gpio_num_t)CONFIG_APP_L293D_IN1_GPIO, phase->in1);
  gpio_set_level((gpio_num_t)CONFIG_APP_L293D_IN2_GPIO, phase->in2);
  gpio_set_level((gpio_num_t)CONFIG_APP_L293D_IN3_GPIO, phase->in3);
  gpio_set_level((gpio_num_t)CONFIG_APP_L293D_IN4_GPIO, phase->in4);

  s_stepper.coils_enabled = true;
  app_stepper_led_toggle();
}

static void app_stepper_release(void) {
  gpio_set_level((gpio_num_t)CONFIG_APP_L293D_IN1_GPIO, 0);
  gpio_set_level((gpio_num_t)CONFIG_APP_L293D_IN2_GPIO, 0);
  gpio_set_level((gpio_num_t)CONFIG_APP_L293D_IN3_GPIO, 0);
  gpio_set_level((gpio_num_t)CONFIG_APP_L293D_IN4_GPIO, 0);

  s_stepper.coils_enabled = false;
  s_stepper.led_state = false;
  app_stepper_led_set(false);
}

static void app_stepper_step_forward_once(void) {
  const size_t phase_count = sizeof(s_phases) / sizeof(s_phases[0]);

  app_stepper_apply_phase(&s_phases[s_stepper.phase_index]);
  s_stepper.phase_index = (s_stepper.phase_index + 1U) % phase_count;
  s_stepper.total_steps++;
}

static void app_stepper_step_reverse_once(void) {
  const size_t phase_count = sizeof(s_phases) / sizeof(s_phases[0]);

  if (s_stepper.phase_index == 0) {
    s_stepper.phase_index = phase_count - 1U;
  } else {
    s_stepper.phase_index--;
  }

  app_stepper_apply_phase(&s_phases[s_stepper.phase_index]);
  s_stepper.total_steps++;
}

static void app_stepper_apply_named_phase(size_t phase_index) {
  const size_t phase_count = sizeof(s_phases) / sizeof(s_phases[0]);

  if (phase_index >= phase_count) {
    return;
  }

  app_stepper_set_mode(APP_STEPPER_MODE_STOP);
  s_stepper.phase_index = phase_index;
  app_stepper_apply_phase(&s_phases[phase_index]);

  ESP_LOGI(TAG,
           "hold %s: in1=%u in2=%u in3=%u in4=%u",
           s_phases[phase_index].label,
           s_phases[phase_index].in1,
           s_phases[phase_index].in2,
           s_phases[phase_index].in3,
           s_phases[phase_index].in4);
  app_stepper_emit_telemetry("hold_phase");
}

static void app_stepper_set_mode(app_stepper_mode_t mode) {
  if (s_stepper.mode == mode) {
    return;
  }

  s_stepper.mode = mode;
  s_stepper.pause_started_ms = 0;
  s_stepper.moved_steps_in_leg = 0;

  ESP_LOGI(TAG,
           "%smode -> %s%s",
           APP_STEPPER_COLOR_OK,
           app_stepper_mode_to_str(mode),
           APP_STEPPER_COLOR_RESET);

  if (mode == APP_STEPPER_MODE_STOP) {
    app_stepper_release();
    app_stepper_emit_telemetry("mode_stop");
    return;
  }

  /* Make the next tick step immediately after a mode switch. */
  s_stepper.last_step_ms = 0;
  app_stepper_emit_telemetry("mode_change");
}

static void app_stepper_handle_command(uint8_t cmd) {
  const uint32_t now_ms = esp_log_timestamp();

  if (cmd == s_stepper.last_cmd &&
      (now_ms - s_stepper.last_cmd_ms) < APP_STEPPER_DUPLICATE_CMD_GUARD_MS) {
    return;
  }

  s_stepper.last_cmd = cmd;
  s_stepper.last_cmd_ms = now_ms;

  switch (cmd) {
    case 'h':
    case 'H':
      app_stepper_print_help();
      break;

    case 'p':
    case 'P':
      app_stepper_print_status();
      break;

    case 's':
    case 'S':
      app_stepper_set_mode(APP_STEPPER_MODE_STOP);
      break;

    case 'f':
    case 'F':
      app_stepper_set_mode(APP_STEPPER_MODE_FORWARD);
      break;

    case 'r':
    case 'R':
      app_stepper_set_mode(APP_STEPPER_MODE_REVERSE);
      break;

    case 'w':
    case 'W':
      s_stepper.sweep_state = APP_STEPPER_SWEEP_FORWARD;
      app_stepper_set_mode(APP_STEPPER_MODE_SWEEP);
      break;

    case '1':
      app_stepper_step_forward_once();
      app_stepper_print_status();
      break;

    case '2':
      app_stepper_step_reverse_once();
      app_stepper_print_status();
      break;

    case 'a':
    case 'A':
      app_stepper_apply_named_phase(0);
      break;

    case 'b':
    case 'B':
      app_stepper_apply_named_phase(1);
      break;

    case 'c':
    case 'C':
      app_stepper_apply_named_phase(2);
      break;

    case 'd':
    case 'D':
      app_stepper_apply_named_phase(3);
      break;

    case '+':
    case '=': {
      const uint32_t delta_ms = app_stepper_delay_adjust_delta_ms(s_stepper.step_delay_ms);
      if (s_stepper.step_delay_ms > APP_STEPPER_MIN_DELAY_MS) {
        const uint32_t next_delay =
          (s_stepper.step_delay_ms > (APP_STEPPER_MIN_DELAY_MS + delta_ms))
            ? (s_stepper.step_delay_ms - delta_ms)
            : APP_STEPPER_MIN_DELAY_MS;
        s_stepper.step_delay_ms = next_delay;
      }
      app_stepper_log_timing("faster");
      break;
    }

    case '-':
    case '_': {
      const uint32_t delta_ms = app_stepper_delay_adjust_delta_ms(s_stepper.step_delay_ms);
      const uint32_t remaining_ms = APP_STEPPER_MAX_DELAY_MS - s_stepper.step_delay_ms;
      s_stepper.step_delay_ms += (delta_ms < remaining_ms) ? delta_ms : remaining_ms;
      app_stepper_log_timing("slower");
      break;
    }

    case 'z':
    case 'Z':
      app_stepper_release();
      ESP_LOGI(TAG, "%scoils released%s", APP_STEPPER_COLOR_WARN, APP_STEPPER_COLOR_RESET);
      app_stepper_emit_telemetry("release");
      break;

    case '\r':
    case '\n':
      break;

    default:
      ESP_LOGW(TAG, "unknown command: 0x%02X ('%c')", cmd, (cmd >= 32U && cmd <= 126U) ? cmd : '.');
      break;
  }
}

static void app_stepper_handle_uart(void) {
  uint8_t buf[16] = {0};

  int len = uart_read_bytes(APP_STEPPER_UART_PORT, buf, sizeof(buf), 0);
  if (len <= 0) {
    return;
  }

  for (int i = 0; i < len; i++) {
    app_stepper_handle_command(buf[i]);
  }
}

esp_err_t app_stepper_init(void) {
  app_stepper_log_block("L293D STEPPER UART CONTROL");

  esp_err_t err = app_stepper_gpio_init();
  if (err != ESP_OK) {
    ESP_LOGE(TAG, "gpio init failed: %s", esp_err_to_name(err));
    return err;
  }

  app_stepper_led_init();
  app_stepper_release();

  err = app_stepper_uart_init();
  if (err != ESP_OK) {
    ESP_LOGW(TAG, "uart control disabled, motor logic still available");
    s_stepper.uart_ready = false;
  }

  ESP_LOGI(TAG,
           "pins: in1=%d in2=%d in3=%d in4=%d",
           CONFIG_APP_L293D_IN1_GPIO,
           CONFIG_APP_L293D_IN2_GPIO,
           CONFIG_APP_L293D_IN3_GPIO,
           CONFIG_APP_L293D_IN4_GPIO);
  ESP_LOGI(TAG, "step delay: %" PRIu32 " ms", s_stepper.step_delay_ms);
  ESP_LOGI(TAG, "uart: num=%d baud=%d ready=%s",
           APP_STEPPER_UART_PORT,
           CONFIG_APP_STEPPER_UART_BAUD_RATE,
           s_stepper.uart_ready ? "yes" : "no");
  ESP_LOGI(TAG, "EN1,2 and EN3,4 must be tied HIGH");

#if CONFIG_APP_STEPPER_LED_ENABLE
  ESP_LOGI(TAG, "stepper led gpio=%d", CONFIG_APP_STEPPER_LED_GPIO);
#endif

  app_stepper_print_help();

  s_stepper.sweep_state = APP_STEPPER_SWEEP_FORWARD;
  app_stepper_set_mode(APP_STEPPER_MODE_SWEEP);
  app_stepper_emit_telemetry("init");

  return ESP_OK;
}

void app_stepper_tick(void) {
  const uint32_t now_ms = esp_log_timestamp();

  if (s_stepper.uart_ready) {
    app_stepper_handle_uart();
  }

  if ((now_ms - s_stepper.last_telemetry_ms) >= 1000U) {
    s_stepper.last_telemetry_ms = now_ms;
    app_stepper_emit_telemetry("heartbeat");
  }

  if (s_stepper.mode == APP_STEPPER_MODE_STOP) {
    return;
  }

  if (s_stepper.mode == APP_STEPPER_MODE_SWEEP) {
    if (s_stepper.sweep_state == APP_STEPPER_SWEEP_PAUSE_AFTER_FORWARD ||
        s_stepper.sweep_state == APP_STEPPER_SWEEP_PAUSE_AFTER_REVERSE) {
      if (s_stepper.pause_started_ms == 0U) {
        s_stepper.pause_started_ms = now_ms;
        app_stepper_release();
      }

      if ((now_ms - s_stepper.pause_started_ms) < APP_STEPPER_EDGE_PAUSE_MS) {
        return;
      }

      s_stepper.pause_started_ms = 0;
      s_stepper.moved_steps_in_leg = 0;

      if (s_stepper.sweep_state == APP_STEPPER_SWEEP_PAUSE_AFTER_FORWARD) {
        s_stepper.sweep_state = APP_STEPPER_SWEEP_REVERSE;
        ESP_LOGI(TAG, "sweep -> reverse");
      } else {
        s_stepper.sweep_state = APP_STEPPER_SWEEP_FORWARD;
        ESP_LOGI(TAG, "sweep -> forward");
      }
      app_stepper_emit_telemetry("sweep_edge");
    }

    if ((now_ms - s_stepper.last_step_ms) < s_stepper.step_delay_ms) {
      return;
    }

    s_stepper.last_step_ms = now_ms;

    if (s_stepper.sweep_state == APP_STEPPER_SWEEP_FORWARD) {
      app_stepper_step_forward_once();
      s_stepper.moved_steps_in_leg++;

      if (s_stepper.moved_steps_in_leg >= APP_STEPPER_SWEEP_STEPS) {
        s_stepper.sweep_state = APP_STEPPER_SWEEP_PAUSE_AFTER_FORWARD;
      }
      return;
    }

    if (s_stepper.sweep_state == APP_STEPPER_SWEEP_REVERSE) {
      app_stepper_step_reverse_once();
      s_stepper.moved_steps_in_leg++;

      if (s_stepper.moved_steps_in_leg >= APP_STEPPER_SWEEP_STEPS) {
        s_stepper.sweep_state = APP_STEPPER_SWEEP_PAUSE_AFTER_REVERSE;
      }
      return;
    }

    return;
  }

  if ((now_ms - s_stepper.last_step_ms) < s_stepper.step_delay_ms) {
    return;
  }

  s_stepper.last_step_ms = now_ms;

  if (s_stepper.mode == APP_STEPPER_MODE_FORWARD) {
    app_stepper_step_forward_once();
    return;
  }

  if (s_stepper.mode == APP_STEPPER_MODE_REVERSE) {
    app_stepper_step_reverse_once();
    return;
  }
}
