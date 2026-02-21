#include "app.h"
#include "esp_log.h"
#include "sdkconfig.h"
#include "i2c_bus.h"

static const char *TAG = "app";
static int s_counter = 0;

void app_init(void) {
  ESP_LOGI(TAG, "init");

  esp_err_t err = i2c_bus_init();
  if (err != ESP_OK) {
    ESP_LOGE(TAG, "i2c init failed: %s", esp_err_to_name(err));
    return;
  }

  i2c_bus_scan();
}

void app_tick(void) {
  s_counter++;
#if CONFIG_APP_TICK_LOG
  ESP_LOGI(TAG, "tick %d", s_counter);
#endif
}