#pragma once

#include <stdint.h>
#include "esp_err.h"

typedef struct {
  int sda_io_num;
  int scl_io_num;
  uint32_t freq_hz;
} i2c_bus_config_t;

esp_err_t i2c_bus_init(const i2c_bus_config_t *cfg);
void i2c_bus_deinit(void);

esp_err_t i2c_bus_scan(uint8_t *found_addrs, int max_addrs, int *found_cnt);

esp_err_t i2c_bus_probe_addr(uint8_t addr);
esp_err_t i2c_bus_read(uint8_t addr, uint8_t reg, void *out, size_t out_len);
esp_err_t i2c_bus_write(uint8_t addr, uint8_t reg, const void *data, size_t len);