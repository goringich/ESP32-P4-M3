#pragma once

#include <stdint.h>

#include "esp_err.h"

esp_err_t mpu9250_probe_addr(uint8_t *out_addr);
esp_err_t mpu9250_read_whoami(uint8_t addr, uint8_t *out_whoami);
esp_err_t mpu9250_probe_and_read_whoami(uint8_t *out_addr, uint8_t *out_whoami);
const char *mpu9250_whoami_name(uint8_t whoami);
