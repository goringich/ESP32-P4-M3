#pragma once

#include "esp_err.h"

#include "app.h"

esp_err_t app_ble_init(void);
void app_ble_tick(void);
void app_ble_get_status(app_ble_status_t *status);
