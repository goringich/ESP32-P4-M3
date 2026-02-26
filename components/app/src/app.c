#include "app.h"

#include <stdint.h>

#include "esp_log.h"
#include "sdkconfig.h"

#include "i2c_bus.h"
#include "i2c_bus_diag.h"
#include "mpu9250.h"

static const char *TAG = "app";
static void app_mpu_whoami_check(void);

static void app_mpu_whoami_check(void) {
  uint8_t addr = 0;
  uint8_t who = 0;

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

  ESP_LOGI(TAG, "init");

  esp_err_t err = i2c_bus_init();
  if (err != ESP_OK) {
    ESP_LOGE(TAG, "i2c init failed: %s", esp_err_to_name(err));
    return;
  }

  err = i2c_bus_scan();
  if (err != ESP_OK) {
    ESP_LOGE(TAG, "i2c scan failed: %s", esp_err_to_name(err));
  }

  app_mpu_whoami_check();
}

void app_tick(void) {
#if CONFIG_APP_TICK_LOG
  static int s_counter = 0;
  s_counter++;
  if ((s_counter % 5) == 0) {
    ESP_LOGI(TAG, "tick %d", s_counter);
  }
#endif
}
