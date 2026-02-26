#include "i2c_bus.h"

#include <stdbool.h>
#include <stdio.h>

#include "driver/gpio.h"
#include "driver/i2c_master.h"

#include "esp_log.h"
#include "esp_rom_sys.h"
#include "sdkconfig.h"

static const char *TAG = "i2c_bus";
static i2c_master_bus_handle_t s_bus = NULL;
static const int I2C_XFER_TIMEOUT_MS = 200;

typedef struct {
  int sda;
  int scl;
} i2c_lines_t;

static i2c_lines_t i2c_bus_read_lines(void);
static void i2c_bus_log_lines(const char *where, i2c_lines_t l);
static esp_err_t i2c_bus_open_device(uint8_t addr, i2c_master_dev_handle_t *out_dev);

#if CONFIG_I2C_BUS_SCAN_TABLE
static void i2c_bus_log_scan_table(const bool present[128]);
#endif

#if CONFIG_I2C_BUS_SELFTEST
static bool i2c_bus_selfcheck_gpio(const char *where);
#endif

esp_err_t i2c_bus_init(void) {
  if (s_bus != NULL) {
    ESP_LOGD(TAG, "init: already ready");
    return ESP_OK;
  }

#if CONFIG_I2C_BUS_SELFTEST
  if (!i2c_bus_selfcheck_gpio("init")) {
    ESP_LOGW(TAG, "init: selftest failed (pins/wiring/pullups)");
  }
#endif

  /* Read idle levels before attaching I2C peripheral; these helpers switch pin modes. */
  i2c_lines_t l = i2c_bus_read_lines();
  i2c_bus_log_lines("init: idle lines", l);
  if (l.sda == 0 || l.scl == 0) {
    ESP_LOGW(TAG, "init: idle low -> wiring/pullups/power");
  }

  i2c_master_bus_config_t bus_cfg = {
    .i2c_port = -1,
    .sda_io_num = CONFIG_I2C_BUS_SDA_GPIO,
    .scl_io_num = CONFIG_I2C_BUS_SCL_GPIO,
    .clk_source = I2C_CLK_SRC_DEFAULT,
    .glitch_ignore_cnt = 7,
    .intr_priority = 0,
    .trans_queue_depth = 0,
    .flags = {
      .enable_internal_pullup = 1,
    },
  };

  esp_err_t err = i2c_new_master_bus(&bus_cfg, &s_bus);
  if (err != ESP_OK) {
    ESP_LOGE(TAG, "init: i2c_new_master_bus failed: %s", esp_err_to_name(err));
    return err;
  }

  ESP_LOGI(TAG, "init: bus ready sda=%d scl=%d freq=%d",
    CONFIG_I2C_BUS_SDA_GPIO,
    CONFIG_I2C_BUS_SCL_GPIO,
    CONFIG_I2C_BUS_FREQ_HZ
  );

  return ESP_OK;
}

void i2c_bus_deinit(void) {
  if (s_bus == NULL) {
    return;
  }

  esp_err_t err = i2c_del_master_bus(s_bus);
  if (err != ESP_OK) {
    ESP_LOGW(TAG, "deinit: i2c_del_master_bus failed: %s", esp_err_to_name(err));
    return;
  }

  s_bus = NULL;
  ESP_LOGI(TAG, "deinit: bus released");
}

esp_err_t i2c_bus_scan(void) {
  if (s_bus == NULL) {
    ESP_LOGE(TAG, "scan: bus not initialized");
    return ESP_ERR_INVALID_STATE;
  }

  /* Do not repurpose SDA/SCL as plain GPIO here: it detaches the active I2C peripheral. */

  esp_log_level_set("i2c.master", ESP_LOG_ERROR);

#if CONFIG_I2C_BUS_SCAN_TABLE
  bool present[128] = {0};
#endif

  int found = 0;
  int timeouts = 0;
  int other_err = 0;

  ESP_LOGI(TAG, "scan: quick probe 0x68/0x69");
  for (uint8_t addr = 0x68; addr <= 0x69; addr++) {
    esp_err_t err = i2c_master_probe(s_bus, addr, 200);
    if (err == ESP_OK) {
      found++;
#if CONFIG_I2C_BUS_SCAN_TABLE
      present[addr] = true;
#endif
      ESP_LOGI(TAG, "scan: found 0x%02X", addr);
    } else if (err == ESP_ERR_TIMEOUT) {
      timeouts++;
    } else {
      other_err++;
    }
  }

#if CONFIG_I2C_BUS_SCAN_FULL
  ESP_LOGI(TAG, "scan: full probe 0x03..0x77");
  for (uint8_t addr = 0x03; addr <= 0x77; addr++) {
    esp_err_t err = i2c_master_probe(s_bus, addr, 50);
    if (err == ESP_OK) {
      found++;
#if CONFIG_I2C_BUS_SCAN_TABLE
      present[addr] = true;
#endif
    } else if (err == ESP_ERR_TIMEOUT) {
      timeouts++;
    } else {
      other_err++;
    }
  }
#endif

  ESP_LOGI(TAG, "scan: result found=%d timeouts=%d other_err=%d", found, timeouts, other_err);

#if CONFIG_I2C_BUS_SCAN_TABLE
  i2c_bus_log_scan_table(present);
#endif

  if (found == 0) {
    ESP_LOGW(TAG, "scan: no devices found");
    ESP_LOGW(TAG, "scan: check GND/VCC, SDA/SCL swapped, pullups, correct header pins");
  }

  return ESP_OK;
}

esp_err_t i2c_bus_probe_addr(uint8_t addr) {
  if (s_bus == NULL) {
    return ESP_ERR_INVALID_STATE;
  }

  return i2c_master_probe(s_bus, addr, I2C_XFER_TIMEOUT_MS);
}

esp_err_t i2c_bus_read(uint8_t addr, uint8_t reg, void *out, size_t out_len) {
  if (s_bus == NULL) {
    return ESP_ERR_INVALID_STATE;
  }
  if (out == NULL || out_len == 0) {
    return ESP_ERR_INVALID_ARG;
  }

  i2c_master_dev_handle_t dev = NULL;
  esp_err_t err = i2c_bus_open_device(addr, &dev);
  if (err != ESP_OK) {
    return err;
  }

  err = i2c_master_transmit_receive(dev, &reg, 1, (uint8_t *)out, out_len, I2C_XFER_TIMEOUT_MS);
  esp_err_t rm_err = i2c_master_bus_rm_device(dev);
  if (err == ESP_OK && rm_err != ESP_OK) {
    return rm_err;
  }
  return err;
}

esp_err_t i2c_bus_write(uint8_t addr, uint8_t reg, const void *data, size_t len) {
  if (s_bus == NULL) {
    return ESP_ERR_INVALID_STATE;
  }
  if (data == NULL && len > 0) {
    return ESP_ERR_INVALID_ARG;
  }

  uint8_t buf[1 + 16];
  if (len > 16) {
    return ESP_ERR_INVALID_SIZE;
  }

  buf[0] = reg;
  for (size_t i = 0; i < len; i++) {
    buf[1 + i] = ((const uint8_t *)data)[i];
  }

  i2c_master_dev_handle_t dev = NULL;
  esp_err_t err = i2c_bus_open_device(addr, &dev);
  if (err != ESP_OK) {
    return err;
  }

  err = i2c_master_transmit(dev, buf, 1 + len, I2C_XFER_TIMEOUT_MS);
  esp_err_t rm_err = i2c_master_bus_rm_device(dev);
  if (err == ESP_OK && rm_err != ESP_OK) {
    return rm_err;
  }
  return err;
}

static esp_err_t i2c_bus_open_device(uint8_t addr, i2c_master_dev_handle_t *out_dev) {
  if (s_bus == NULL || out_dev == NULL) {
    return ESP_ERR_INVALID_ARG;
  }

  i2c_device_config_t dev_cfg = {
    .dev_addr_length = I2C_ADDR_BIT_LEN_7,
    .device_address = addr,
    .scl_speed_hz = CONFIG_I2C_BUS_FREQ_HZ,
    .scl_wait_us = 0,
    .flags = {
      .disable_ack_check = 0,
    },
  };

  return i2c_master_bus_add_device(s_bus, &dev_cfg, out_dev);
}

static i2c_lines_t i2c_bus_read_lines(void) {
  gpio_set_direction(CONFIG_I2C_BUS_SDA_GPIO, GPIO_MODE_INPUT);
  gpio_set_direction(CONFIG_I2C_BUS_SCL_GPIO, GPIO_MODE_INPUT);

  i2c_lines_t l = {
    .sda = gpio_get_level(CONFIG_I2C_BUS_SDA_GPIO),
    .scl = gpio_get_level(CONFIG_I2C_BUS_SCL_GPIO),
  };
  return l;
}

static void i2c_bus_log_lines(const char *where, i2c_lines_t l) {
  ESP_LOGI(TAG, "%s: sda(gpio=%d)=%d scl(gpio=%d)=%d",
    where,
    CONFIG_I2C_BUS_SDA_GPIO, l.sda,
    CONFIG_I2C_BUS_SCL_GPIO, l.scl
  );
}

#if CONFIG_I2C_BUS_SCAN_TABLE
static void i2c_bus_log_scan_table(const bool present[128]) {
  ESP_LOGI(TAG, "scan table:");
  ESP_LOGI(TAG, "     00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F");

  for (int row = 0; row < 8; row++) {
    char line[256];
    int off = 0;

    off += snprintf(line + off, sizeof(line) - off, "%02X: ", row << 4);

    for (int col = 0; col < 16; col++) {
      int addr = (row << 4) | col;

      if (addr < 0x03 || addr > 0x77) {
        off += snprintf(line + off, sizeof(line) - off, " ..");
        continue;
      }

      off += snprintf(line + off, sizeof(line) - off, present[addr] ? " %02X" : " --", addr);
    }

    ESP_LOGI(TAG, "%s", line);
  }
}
#endif

#if CONFIG_I2C_BUS_SELFTEST
static bool i2c_bus_selfcheck_gpio(const char *where) {
  const gpio_num_t sda = (gpio_num_t)CONFIG_I2C_BUS_SDA_GPIO;
  const gpio_num_t scl = (gpio_num_t)CONFIG_I2C_BUS_SCL_GPIO;

  gpio_set_direction(sda, GPIO_MODE_INPUT);
  gpio_set_direction(scl, GPIO_MODE_INPUT);

  int sda_idle = gpio_get_level(sda);
  int scl_idle = gpio_get_level(scl);

  ESP_LOGI(TAG, "%s: selftest idle sda=%d scl=%d", where, sda_idle, scl_idle);

  if (sda_idle == 0 || scl_idle == 0) {
    ESP_LOGW(TAG, "%s: selftest fail: idle low", where);
    return false;
  }

  gpio_config_t cfg = {
    .pin_bit_mask = (1ULL << sda) | (1ULL << scl),
    .mode = GPIO_MODE_OUTPUT_OD,
    .pull_up_en = GPIO_PULLUP_ENABLE,
    .pull_down_en = GPIO_PULLDOWN_DISABLE,
    .intr_type = GPIO_INTR_DISABLE,
  };
  gpio_config(&cfg);

  gpio_set_level(sda, 1);
  gpio_set_level(scl, 1);
  esp_rom_delay_us(5);

  gpio_set_level(scl, 0);
  esp_rom_delay_us(5);
  int scl_low = gpio_get_level(scl);

  gpio_set_level(scl, 1);
  esp_rom_delay_us(50);
  int scl_high = gpio_get_level(scl);

  gpio_set_direction(sda, GPIO_MODE_INPUT);
  gpio_set_direction(scl, GPIO_MODE_INPUT);

  ESP_LOGI(TAG, "%s: selftest scl_low=%d scl_high=%d", where, scl_low, scl_high);

  if (scl_low != 0) {
    ESP_LOGE(TAG, "%s: selftest fail: cannot drive SCL low", where);
    return false;
  }
  if (scl_high != 1) {
    ESP_LOGE(TAG, "%s: selftest fail: SCL not returning high", where);
    return false;
  }

  return true;
}
#endif
