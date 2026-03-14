#pragma once

#include <stdint.h>

#include "esp_err.h"

esp_err_t app_mpu_pretty_init(void);
esp_err_t app_mpu_pretty_log_line(uint32_t tick_counter, uint32_t uptime_ms);
