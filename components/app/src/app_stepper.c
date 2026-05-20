#include "app_stepper.h"

#include <inttypes.h>
#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#if CONFIG_APP_CONTROL_ENABLE
#include "app_control.h"
#endif

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
#define APP_STEPPER_DUPLICATE_CMD_GUARD_MS 150U
#define APP_STEPPER_STABILIZE_DEADBAND_RATIO 0.15f
#define APP_STEPPER_STABILIZE_MAX_BUDGET_MS 120.0f

#ifdef CONFIG_APP_L293D_LEFT_INVERT
#define APP_STEPPER_LEFT_INVERT true
#else
#define APP_STEPPER_LEFT_INVERT false
#endif

#ifdef CONFIG_APP_L293D_RIGHT_INVERT
#define APP_STEPPER_RIGHT_INVERT true
#else
#define APP_STEPPER_RIGHT_INVERT false
#endif

static const char *TAG = "app_stepper";

typedef enum {
  APP_STEPPER_MODE_STOP = 0,
  APP_STEPPER_MODE_FORWARD,
  APP_STEPPER_MODE_REVERSE,
  APP_STEPPER_MODE_LEFT,
  APP_STEPPER_MODE_RIGHT,
  APP_STEPPER_MODE_STABILIZE,
} app_stepper_mode_t;

typedef struct {
  app_stepper_mode_t mode;
  uint32_t step_delay_ms;
  uint32_t total_steps;
  uint32_t last_cmd_ms;
  uint32_t last_telemetry_ms;
  bool coils_enabled;
  bool uart_ready;
  bool led_state;
  uint8_t in1_level;
  uint8_t in2_level;
  uint8_t in3_level;
  uint8_t in4_level;
  uint8_t last_cmd;
  int8_t left_direction;
  int8_t right_direction;
  float stabilize_velocity_sps;
  float stabilize_drive_budget_ms;
  uint32_t stabilize_last_tick_ms;
} app_stepper_state_t;

static void app_stepper_log_block(const char *title);
static const char *app_stepper_mode_to_str(app_stepper_mode_t mode);
static const char *app_stepper_motor_to_str(int8_t direction);
static void app_stepper_print_help(void);
static void app_stepper_print_status(void);
static void app_stepper_emit_telemetry(const char *reason);

static esp_err_t app_stepper_gpio_init(void);
static esp_err_t app_stepper_uart_init(void);
static void app_stepper_led_init(void);
static void app_stepper_led_set(bool on);

static void app_stepper_apply_drive(int8_t left_direction, int8_t right_direction);
static void app_stepper_apply_channel(int gpio_a, int gpio_b, int8_t direction,
                                      bool invert, uint8_t *out_a, uint8_t *out_b);
static void app_stepper_release(void);
static void app_stepper_set_mode(app_stepper_mode_t mode);
static void app_stepper_handle_uart(void);
static void app_stepper_handle_command(uint8_t cmd);

static app_stepper_state_t s_stepper = {
  .mode = APP_STEPPER_MODE_STOP,
  .step_delay_ms = CONFIG_APP_L293D_STEP_DELAY_MS,
  .total_steps = 0,
  .last_cmd_ms = 0,
  .last_telemetry_ms = 0,
  .coils_enabled = false,
  .uart_ready = false,
  .led_state = false,
  .in1_level = 0,
  .in2_level = 0,
  .in3_level = 0,
  .in4_level = 0,
  .last_cmd = 0,
  .left_direction = 0,
  .right_direction = 0,
  .stabilize_velocity_sps = 0.0f,
  .stabilize_drive_budget_ms = 0.0f,
  .stabilize_last_tick_ms = 0,
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
    case APP_STEPPER_MODE_LEFT:
      return "left";
    case APP_STEPPER_MODE_RIGHT:
      return "right";
    case APP_STEPPER_MODE_STABILIZE:
      return "stabilize";
    default:
      return "unknown";
  }
}

static const char *app_stepper_motor_to_str(int8_t direction) {
  if (direction > 0) {
    return "forward";
  }
  if (direction < 0) {
    return "reverse";
  }
  return "stop";
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
         "\"sweep_state\":\"none\",\"step_delay_ms\":%" PRIu32 ",\"steps_per_second\":%.2f,"
         "\"phase_index\":0,\"total_steps\":%" PRIu32 ",\"coils_enabled\":%s,"
         "\"sweep_steps\":0,\"uart_ready\":%s,\"last_command\":\"%s\","
         "\"left_state\":\"%s\",\"right_state\":\"%s\","
         "\"left_direction\":%d,\"right_direction\":%d,"
         "\"motors\":{\"left\":{\"state\":\"%s\",\"direction\":%d},"
         "\"right\":{\"state\":\"%s\",\"direction\":%d}},"
         "\"pins\":{\"in1\":%u,\"in2\":%u,\"in3\":%u,\"in4\":%u},"
         "\"gpio_pins\":{\"in1\":%d,\"in2\":%d,\"in3\":%d,\"in4\":%d},\"led_gpio\":%d}\n",
         reason != NULL ? reason : "update",
         app_stepper_mode_to_str(s_stepper.mode),
         s_stepper.step_delay_ms,
         (double)fabsf(s_stepper.stabilize_velocity_sps),
         s_stepper.total_steps,
         s_stepper.coils_enabled ? "true" : "false",
         s_stepper.uart_ready ? "true" : "false",
         app_stepper_cmd_to_str(s_stepper.last_cmd),
         app_stepper_motor_to_str(s_stepper.left_direction),
         app_stepper_motor_to_str(s_stepper.right_direction),
         (int)s_stepper.left_direction,
         (int)s_stepper.right_direction,
         app_stepper_motor_to_str(s_stepper.left_direction),
         (int)s_stepper.left_direction,
         app_stepper_motor_to_str(s_stepper.right_direction),
         (int)s_stepper.right_direction,
         (unsigned)s_stepper.in1_level,
         (unsigned)s_stepper.in2_level,
         (unsigned)s_stepper.in3_level,
         (unsigned)s_stepper.in4_level,
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

static void app_stepper_print_help(void) {
  ESP_LOGI(TAG, "%scommands%s", APP_STEPPER_COLOR_CMD, APP_STEPPER_COLOR_RESET);
  ESP_LOGI(TAG, "  h : print help");
  ESP_LOGI(TAG, "  p : print status");
  ESP_LOGI(TAG, "  s : stop both motors");
  ESP_LOGI(TAG, "  f : both motors forward");
  ESP_LOGI(TAG, "  r : both motors reverse");
  ESP_LOGI(TAG, "  2 : turn left  (left reverse, right forward)");
  ESP_LOGI(TAG, "  1 : turn right (left forward, right reverse)");
  ESP_LOGI(TAG, "  g : stabilization demo (forward/reverse by PID sign)");
  ESP_LOGI(TAG, "  z : release both channels");
}

static void app_stepper_print_status(void) {
  ESP_LOGI(TAG,
           "status: mode=%s left=%s(%d) right=%s(%d) total_moves=%" PRIu32
           " uart=%s pins=%u/%u/%u/%u",
           app_stepper_mode_to_str(s_stepper.mode),
           app_stepper_motor_to_str(s_stepper.left_direction),
           (int)s_stepper.left_direction,
           app_stepper_motor_to_str(s_stepper.right_direction),
           (int)s_stepper.right_direction,
           s_stepper.total_steps,
           s_stepper.uart_ready ? "ready" : "off",
           (unsigned)s_stepper.in1_level,
           (unsigned)s_stepper.in2_level,
           (unsigned)s_stepper.in3_level,
           (unsigned)s_stepper.in4_level);
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
  s_stepper.led_state = on;
  gpio_set_level((gpio_num_t)CONFIG_APP_STEPPER_LED_GPIO, on ? 1 : 0);
#else
  (void)on;
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

static void app_stepper_apply_channel(int gpio_a, int gpio_b, int8_t direction,
                                      bool invert, uint8_t *out_a, uint8_t *out_b) {
  uint8_t level_a = 0;
  uint8_t level_b = 0;
  int8_t effective = direction;

  if (invert) {
    effective = (int8_t)-effective;
  }

  if (effective > 0) {
    level_a = 1;
    level_b = 0;
  } else if (effective < 0) {
    level_a = 0;
    level_b = 1;
  }

  gpio_set_level((gpio_num_t)gpio_a, level_a);
  gpio_set_level((gpio_num_t)gpio_b, level_b);
  *out_a = level_a;
  *out_b = level_b;
}

static void app_stepper_apply_drive(int8_t left_direction, int8_t right_direction) {
  app_stepper_apply_channel(CONFIG_APP_L293D_IN1_GPIO,
                            CONFIG_APP_L293D_IN2_GPIO,
                            left_direction,
                            APP_STEPPER_LEFT_INVERT,
                            &s_stepper.in1_level,
                            &s_stepper.in2_level);
  app_stepper_apply_channel(CONFIG_APP_L293D_IN3_GPIO,
                            CONFIG_APP_L293D_IN4_GPIO,
                            right_direction,
                            APP_STEPPER_RIGHT_INVERT,
                            &s_stepper.in3_level,
                            &s_stepper.in4_level);

  s_stepper.left_direction = left_direction;
  s_stepper.right_direction = right_direction;
  s_stepper.coils_enabled = (left_direction != 0) || (right_direction != 0);
  app_stepper_led_set(s_stepper.coils_enabled);
}

static void app_stepper_release(void) {
  app_stepper_apply_drive(0, 0);
}

static void app_stepper_set_mode(app_stepper_mode_t mode) {
  s_stepper.mode = mode;

  switch (mode) {
    case APP_STEPPER_MODE_STOP:
      app_stepper_release();
      break;
    case APP_STEPPER_MODE_FORWARD:
      app_stepper_apply_drive(1, 1);
      s_stepper.total_steps++;
      break;
    case APP_STEPPER_MODE_REVERSE:
      app_stepper_apply_drive(-1, -1);
      s_stepper.total_steps++;
      break;
    case APP_STEPPER_MODE_LEFT:
      app_stepper_apply_drive(-1, 1);
      s_stepper.total_steps++;
      break;
    case APP_STEPPER_MODE_RIGHT:
      app_stepper_apply_drive(1, -1);
      s_stepper.total_steps++;
      break;
    case APP_STEPPER_MODE_STABILIZE:
      s_stepper.stabilize_drive_budget_ms = 0.0f;
      s_stepper.stabilize_last_tick_ms = 0U;
      app_stepper_release();
      break;
    default:
      app_stepper_release();
      break;
  }

  ESP_LOGI(TAG,
           "%smode -> %s | left=%s right=%s%s",
           APP_STEPPER_COLOR_OK,
           app_stepper_mode_to_str(mode),
           app_stepper_motor_to_str(s_stepper.left_direction),
           app_stepper_motor_to_str(s_stepper.right_direction),
           APP_STEPPER_COLOR_RESET);
  app_stepper_emit_telemetry("mode_change");
}

static void app_stepper_handle_command(uint8_t cmd) {
  const uint32_t now_ms = esp_log_timestamp();

  if (cmd == '\r' || cmd == '\n') {
    return;
  }

  if (cmd < 32U || cmd > 126U) {
    return;
  }

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
    case 'z':
    case 'Z':
      app_stepper_set_mode(APP_STEPPER_MODE_STOP);
#if CONFIG_APP_CONTROL_ENABLE
      app_control_set_active(false);
#endif
      break;

    case 'g':
    case 'G':
#if CONFIG_APP_CONTROL_ENABLE
      s_stepper.stabilize_velocity_sps = 0.0f;
      app_stepper_set_mode(APP_STEPPER_MODE_STABILIZE);
      app_control_set_active(true);
      ESP_LOGI(TAG, "stabilize mode enabled");
#else
      ESP_LOGW(TAG, "stabilize not built (APP_CONTROL_ENABLE=n)");
#endif
      break;

    case 'f':
    case 'F':
      app_stepper_set_mode(APP_STEPPER_MODE_FORWARD);
      break;

    case 'r':
    case 'R':
      app_stepper_set_mode(APP_STEPPER_MODE_REVERSE);
      break;

    case '2':
    case 'l':
    case 'L':
      app_stepper_set_mode(APP_STEPPER_MODE_LEFT);
      break;

    case '1':
    case 'q':
    case 'Q':
      app_stepper_set_mode(APP_STEPPER_MODE_RIGHT);
      break;

    case '+':
    case '=':
    case '-':
    case '_':
    case 'w':
    case 'W':
    case 'a':
    case 'A':
    case 'b':
    case 'B':
    case 'c':
    case 'C':
    case 'd':
    case 'D':
      ESP_LOGW(TAG, "command '%c' is disabled in two-wheel drive mode", cmd);
      break;

    default:
      ESP_LOGW(TAG, "unknown command: 0x%02X ('%c')", cmd, (cmd >= 32U && cmd <= 126U) ? cmd : '.');
      break;
  }
}

esp_err_t app_stepper_command_char(char cmd) {
  app_stepper_handle_command((uint8_t)cmd);
  return ESP_OK;
}

void app_stepper_get_snapshot(app_stepper_snapshot_t *snapshot) {
  if (snapshot == NULL) {
    return;
  }

  memset(snapshot, 0, sizeof(*snapshot));
  snapshot->mode = app_stepper_mode_to_str(s_stepper.mode);
  snapshot->sweep_state = "none";
  snapshot->left_motor_state = app_stepper_motor_to_str(s_stepper.left_direction);
  snapshot->right_motor_state = app_stepper_motor_to_str(s_stepper.right_direction);
  snapshot->step_delay_ms = s_stepper.step_delay_ms;
  snapshot->steps_per_second = fabsf(s_stepper.stabilize_velocity_sps);
  snapshot->phase_index = 0;
  snapshot->total_steps = s_stepper.total_steps;
  snapshot->sweep_steps = 0;
  snapshot->coils_enabled = s_stepper.coils_enabled;
  snapshot->uart_ready = s_stepper.uart_ready;
  strlcpy(snapshot->last_command,
          app_stepper_cmd_to_str(s_stepper.last_cmd),
          sizeof(snapshot->last_command));
  snapshot->left_direction = s_stepper.left_direction;
  snapshot->right_direction = s_stepper.right_direction;
  snapshot->in1_level = s_stepper.in1_level;
  snapshot->in2_level = s_stepper.in2_level;
  snapshot->in3_level = s_stepper.in3_level;
  snapshot->in4_level = s_stepper.in4_level;
  snapshot->in1_gpio = CONFIG_APP_L293D_IN1_GPIO;
  snapshot->in2_gpio = CONFIG_APP_L293D_IN2_GPIO;
  snapshot->in3_gpio = CONFIG_APP_L293D_IN3_GPIO;
  snapshot->in4_gpio = CONFIG_APP_L293D_IN4_GPIO;
#if CONFIG_APP_STEPPER_LED_ENABLE
  snapshot->led_gpio = CONFIG_APP_STEPPER_LED_GPIO;
#else
  snapshot->led_gpio = -1;
#endif
}

void app_stepper_set_stabilize_velocity(float steps_per_second) {
  s_stepper.stabilize_velocity_sps = steps_per_second;
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
  app_stepper_log_block("L293D DUAL DRIVE UART CONTROL");

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
           "left motor: in1=%d in2=%d invert=%s",
           CONFIG_APP_L293D_IN1_GPIO,
           CONFIG_APP_L293D_IN2_GPIO,
           APP_STEPPER_LEFT_INVERT ? "yes" : "no");
  ESP_LOGI(TAG,
           "right motor: in3=%d in4=%d invert=%s",
           CONFIG_APP_L293D_IN3_GPIO,
           CONFIG_APP_L293D_IN4_GPIO,
           APP_STEPPER_RIGHT_INVERT ? "yes" : "no");
  ESP_LOGI(TAG, "EN1,2 and EN3,4 must be tied HIGH");

  app_stepper_print_help();
  app_stepper_set_mode(APP_STEPPER_MODE_STOP);
  app_stepper_emit_telemetry("init_idle");

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

  if (s_stepper.mode != APP_STEPPER_MODE_STABILIZE) {
    return;
  }

  if (fabsf(s_stepper.stabilize_velocity_sps) < 0.5f) {
    if (s_stepper.left_direction != 0 || s_stepper.right_direction != 0) {
      app_stepper_release();
      app_stepper_emit_telemetry("stabilize_hold");
    }
    s_stepper.stabilize_drive_budget_ms = 0.0f;
    return;
  }

  uint32_t dt_ms = 5U;
  if (s_stepper.stabilize_last_tick_ms > 0U && now_ms > s_stepper.stabilize_last_tick_ms) {
    dt_ms = now_ms - s_stepper.stabilize_last_tick_ms;
    if (dt_ms > 50U) {
      dt_ms = 50U;
    }
  }
  s_stepper.stabilize_last_tick_ms = now_ms;

#if CONFIG_APP_CONTROL_ENABLE
  const float max_velocity = (float)CONFIG_APP_CONTROL_MAX_OUTPUT_SPS;
#else
  const float max_velocity = 50.0f;
#endif

  float drive_ratio = fabsf(s_stepper.stabilize_velocity_sps) / max_velocity;
  if (drive_ratio > 1.0f) {
    drive_ratio = 1.0f;
  }

  if (drive_ratio < APP_STEPPER_STABILIZE_DEADBAND_RATIO) {
    if (s_stepper.left_direction != 0 || s_stepper.right_direction != 0) {
      app_stepper_release();
      app_stepper_emit_telemetry("stabilize_deadband");
    }
    s_stepper.stabilize_drive_budget_ms = 0.0f;
    return;
  }

  s_stepper.stabilize_drive_budget_ms += drive_ratio * (float)dt_ms;
  if (s_stepper.stabilize_drive_budget_ms > APP_STEPPER_STABILIZE_MAX_BUDGET_MS) {
    s_stepper.stabilize_drive_budget_ms = APP_STEPPER_STABILIZE_MAX_BUDGET_MS;
  }

  if (s_stepper.stabilize_drive_budget_ms < (float)dt_ms) {
    if (s_stepper.left_direction != 0 || s_stepper.right_direction != 0) {
      app_stepper_release();
      app_stepper_emit_telemetry("stabilize_pwm_idle");
    }
    return;
  }

  s_stepper.stabilize_drive_budget_ms -= (float)dt_ms;

  if (s_stepper.stabilize_velocity_sps > 0.0f) {
    if (s_stepper.left_direction != 1 || s_stepper.right_direction != 1) {
      app_stepper_apply_drive(1, 1);
      app_stepper_emit_telemetry("stabilize_forward");
    }
    return;
  }

  if (s_stepper.left_direction != -1 || s_stepper.right_direction != -1) {
    app_stepper_apply_drive(-1, -1);
    app_stepper_emit_telemetry("stabilize_reverse");
  }
}
