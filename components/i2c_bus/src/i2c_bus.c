#include "i2c_bus.h"

#include "esp_log.h"
#include "sdkconfig.h"

#include "driver/i2c_master.h"

static const char *TAG = "i2c_bus";

static i2c_master_bus_handle_t s_bus = NULL;

esp_err_t i2c_bus_init(void) {
  if (s_bus != NULL) {
    return ESP_OK;
  }

  i2c_master_bus_config_t bus_cfg = {
    .i2c_port = -1,
    .sda_io_num = CONFIG_I2C_BUS_SDA_GPIO,
    .scl_io_num = CONFIG_I2C_BUS_SCL_GPIO,
    .clk_source = I2C_CLK_SRC_DEFAULT,
    .glitch_ignore_cnt = 7,
    .intr_priority = 0,
    .trans_queue_depth = 8,
    .flags = {
      .enable_internal_pullup = 1,
    },
  };

  esp_err_t err = i2c_new_master_bus(&bus_cfg, &s_bus);
  if (err != ESP_OK) {
    ESP_LOGE(TAG, "i2c_new_master_bus failed: %s", esp_err_to_name(err));
    return err;
  }

  ESP_LOGI(
    TAG,
    "bus ready: sda=%d scl=%d freq=%d",
    CONFIG_I2C_BUS_SDA_GPIO,
    CONFIG_I2C_BUS_SCL_GPIO,
    CONFIG_I2C_BUS_FREQ_HZ
  );

  return ESP_OK;
}

esp_err_t i2c_bus_scan(void) {
  if (s_bus == NULL) {
    return ESP_ERR_INVALID_STATE;
  }

  int found = 0;

  ESP_LOGI(TAG, "scan: 0x03..0x77");
  for (uint8_t addr = 0x03; addr <= 0x77; addr++) {
    esp_err_t err = i2c_master_probe(s_bus, addr, 50);
    if (err == ESP_OK) {
      found++;
      ESP_LOGI(TAG, "found device at 0x%02X", addr);
    }
  }

  ESP_LOGI(TAG, "scan done: %d device(s)", found);
  return ESP_OK;
}