#include "i2c_bus_diag.h"

#include <stddef.h>
#include <stdint.h>

#include "driver/gpio.h"
#include "driver/i2c_master.h"
#include "esp_log.h"

static const char *TAG = "i2c_bus_diag";

typedef struct {
  int sda;
  int scl;
} diag_i2c_pair_t;

static void i2c_bus_diag_probe_pair(int sda, int scl) {
  if (sda == scl) {
    return;
  }

  gpio_set_direction((gpio_num_t)sda, GPIO_MODE_INPUT);
  gpio_set_direction((gpio_num_t)scl, GPIO_MODE_INPUT);
  int sda_idle = gpio_get_level((gpio_num_t)sda);
  int scl_idle = gpio_get_level((gpio_num_t)scl);

  ESP_LOGI(TAG, "try sda=%d scl=%d idle=(%d,%d)", sda, scl, sda_idle, scl_idle);

  i2c_master_bus_handle_t bus = NULL;
  i2c_master_bus_config_t bus_cfg = {
    .i2c_port = -1,
    .sda_io_num = sda,
    .scl_io_num = scl,
    .clk_source = I2C_CLK_SRC_DEFAULT,
    .glitch_ignore_cnt = 7,
    .intr_priority = 0,
    .trans_queue_depth = 0,
    .flags = {
      .enable_internal_pullup = 1,
    },
  };

  esp_err_t err = i2c_new_master_bus(&bus_cfg, &bus);
  if (err != ESP_OK) {
    ESP_LOGW(TAG, "i2c_new_master_bus sda=%d scl=%d failed: %s", sda, scl, esp_err_to_name(err));
    return;
  }

  for (uint8_t addr = 0x68; addr <= 0x69; addr++) {
    err = i2c_master_probe(bus, addr, 120);
    if (err == ESP_OK) {
      ESP_LOGW(TAG, "FOUND addr=0x%02X on sda=%d scl=%d", addr, sda, scl);
    } else {
      ESP_LOGI(TAG, "probe addr=0x%02X on sda=%d scl=%d -> %s", addr, sda, scl, esp_err_to_name(err));
    }
  }

  err = i2c_del_master_bus(bus);
  if (err != ESP_OK) {
    ESP_LOGW(TAG, "i2c_del_master_bus sda=%d scl=%d failed: %s", sda, scl, esp_err_to_name(err));
  }
}

void i2c_bus_diag_sweep_mpu_pairs(void) {
  static const diag_i2c_pair_t kPairs[] = {
    {1, 2},
    {2, 1},
    {3, 2},
    {2, 3},
    {1, 3},
    {3, 1},
    {4, 2},
    {2, 4},
    {1, 4},
    {4, 1},
    {10, 11},
    {11, 10},
  };

  ESP_LOGW(TAG, "starting MPU I2C pair sweep (0x68/0x69)");
  for (size_t i = 0; i < (sizeof(kPairs) / sizeof(kPairs[0])); i++) {
    i2c_bus_diag_probe_pair(kPairs[i].sda, kPairs[i].scl);
  }
  ESP_LOGW(TAG, "MPU I2C pair sweep done");
}
