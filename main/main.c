#include <stdio.h>

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

#include "app.h"

static const char *TAG = "main";

void app_main(void) {
  ESP_LOGI(TAG, "boot");
  app_init();

  while (1) {
    app_tick();
    vTaskDelay(pdMS_TO_TICKS(1000));
  }
}