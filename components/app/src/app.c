#include "app.h"

#include <inttypes.h>
#include <stdint.h>

#include "esp_log.h"
#include "sdkconfig.h"

#include "i2c_bus.h"
#include "i2c_bus_diag.h"
#include "app_mpu_pretty.h"
#include "app_wifi.h"
#include "mpu9250.h"

#define APP_LOG_COLOR_RESET "\x1b[0m"
#define APP_LOG_COLOR_BLOCK_INIT "\x1b[38;5;33m"   /* blue */
#define APP_LOG_COLOR_BLOCK_SCAN "\x1b[38;5;34m"   /* green */
#define APP_LOG_COLOR_BLOCK_MPU "\x1b[38;5;135m"   /* violet */
#define APP_LOG_COLOR_BLOCK_WIFI "\x1b[38;5;45m"   /* cyan */
#define APP_LOG_COLOR_BLOCK_TICK "\x1b[38;5;178m"  /* amber */

static const char *TAG = "app";
static void app_mpu_whoami_check(void);
static void app_log_color_block(const char *label, const char *color);

static void app_mpu_whoami_check(void) {
  uint8_t addr = 0;
  uint8_t who = 0;

  app_log_color_block("MPU WHOAMI CHECK", APP_LOG_COLOR_BLOCK_MPU);

  esp_err_t err = mpu9250_probe_and_read_whoami(&addr, &who);
  if (err == ESP_OK) {
    ESP_LOGW(TAG, "mpu: addr=0x%02X WHO_AM_I=0x%02X (%s)", addr, who, mpu9250_whoami_name(who));
    return;
  }

  ESP_LOGW(TAG, "mpu: not detected on 0x68/0x69 (%s)", esp_err_to_name(err));

  /* Run a wider pin-pair sweep only when the expected wiring fails. */
  i2c_bus_deinit();
  i2c_bus_diag_sweep_mpu_pairs();
}

void app_init(void) {
  esp_log_level_set("i2c.master", ESP_LOG_ERROR);
  esp_log_level_set("i2c_bus", ESP_LOG_INFO);
  esp_log_level_set("app", ESP_LOG_INFO);

  app_log_color_block("APP INITIALIZATION", APP_LOG_COLOR_BLOCK_INIT);

  ESP_LOGI(TAG, "init");

  esp_err_t err = i2c_bus_init();
  if (err != ESP_OK) {
    ESP_LOGE(TAG, "i2c init failed: %s", esp_err_to_name(err));
    return;
  }

  app_log_color_block("I2C SCAN", APP_LOG_COLOR_BLOCK_SCAN);

  err = i2c_bus_scan();
  if (err != ESP_OK) {
    ESP_LOGE(TAG, "i2c scan failed: %s", esp_err_to_name(err));
  }

  app_mpu_whoami_check();

#if CONFIG_APP_WIFI_SMOKE
  app_log_color_block("WIFI SMOKE TEST", APP_LOG_COLOR_BLOCK_WIFI);
  err = app_wifi_smoke_run();
  if (err != ESP_OK) {
    ESP_LOGW(TAG, "wifi smoke result: %s", esp_err_to_name(err));
  }
#endif
}

void app_tick(void) {
#if CONFIG_APP_TICK_LOG
  static uint32_t s_counter = 0;

  s_counter++;
  if ((s_counter % 5) == 0) {
    const uint32_t uptime_ms = esp_log_timestamp();
    esp_err_t err = app_mpu_pretty_log_line(s_counter, uptime_ms);
    if (err != ESP_OK) {
      ESP_LOGW(TAG,
               "%s tick %" PRIu32 " (mpu log err: %s)%s",
               APP_LOG_COLOR_BLOCK_TICK,
               s_counter,
               esp_err_to_name(err),
               APP_LOG_COLOR_RESET);
    }
  }
#endif
}

static void app_log_color_block(const char *label, const char *color) {
  static const char divider[] = "----------------------------------------";

  ESP_LOGI(TAG, "%s%s%s", color, divider, APP_LOG_COLOR_RESET);
  if (label != NULL && label[0] != '\0') {
    ESP_LOGI(TAG, "%s  %s  %s", color, label, APP_LOG_COLOR_RESET);
  }
  ESP_LOGI(TAG, "%s%s%s", color, divider, APP_LOG_COLOR_RESET);
}
