#!/usr/bin/env python3
"""Compile and exercise the actual I2C bus with deterministic ESP-IDF/FreeRTOS mocks."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/i2c_bus/src/i2c_bus.c"
INCLUDE = ROOT / "components/i2c_bus/include"

HEADERS = {
  "esp_err.h": """
#pragma once
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL -1
#define ESP_ERR_INVALID_STATE 0x103
#define ESP_ERR_INVALID_ARG 0x102
#define ESP_ERR_NO_MEM 0x101
#define ESP_ERR_TIMEOUT 0x107
#define ESP_ERR_INVALID_SIZE 0x104
const char *esp_err_to_name(esp_err_t code);
""",
  "sdkconfig.h": """
#pragma once
#define CONFIG_I2C_BUS_SDA_GPIO 1
#define CONFIG_I2C_BUS_SCL_GPIO 2
#define CONFIG_I2C_BUS_FREQ_HZ 400000
#define CONFIG_I2C_BUS_SCAN_TABLE 0
#define CONFIG_I2C_BUS_SCAN_FULL 0
#define CONFIG_I2C_BUS_SELFTEST 0
""",
  "esp_log.h": """
#pragma once
#define ESP_LOG_ERROR 1
#define ESP_LOGD(...) ((void)0)
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define ESP_LOGE(...) ((void)0)
void esp_log_level_set(const char *tag, int level);
""",
  "esp_rom_sys.h": """
#pragma once
void esp_rom_delay_us(unsigned delay);
""",
  "esp_timer.h": """
#pragma once
#include <stdint.h>
int64_t esp_timer_get_time(void);
""",
  "freertos/FreeRTOS.h": """
#pragma once
#include <stdint.h>
typedef int portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED 0
#define portENTER_CRITICAL(mux) ((void)(mux))
#define portEXIT_CRITICAL(mux) ((void)(mux))
#define pdTRUE 1
#define pdFALSE 0
#define pdMS_TO_TICKS(ms) (ms)
typedef unsigned TickType_t;
""",
  "freertos/semphr.h": """
#pragma once
#include "freertos/FreeRTOS.h"
typedef void *SemaphoreHandle_t;
SemaphoreHandle_t xSemaphoreCreateMutex(void);
int xSemaphoreTake(SemaphoreHandle_t mutex, TickType_t timeout);
int xSemaphoreGive(SemaphoreHandle_t mutex);
void vSemaphoreDelete(SemaphoreHandle_t mutex);
""",
  "driver/gpio.h": """
#pragma once
#include <stdint.h>
typedef int gpio_num_t;
#define GPIO_MODE_INPUT 1
#define GPIO_MODE_OUTPUT_OD 2
#define GPIO_PULLUP_ENABLE 1
#define GPIO_PULLDOWN_DISABLE 0
#define GPIO_INTR_DISABLE 0
typedef struct {
  uint64_t pin_bit_mask;
  int mode;
  int pull_up_en;
  int pull_down_en;
  int intr_type;
} gpio_config_t;
int gpio_set_direction(int pin, int mode);
int gpio_get_level(int pin);
int gpio_config(const gpio_config_t *cfg);
int gpio_set_level(int pin, int level);
""",
  "driver/i2c_master.h": """
#pragma once
#include <stddef.h>
#include <stdint.h>
#include "esp_err.h"
typedef void *i2c_master_bus_handle_t;
typedef void *i2c_master_dev_handle_t;
#define I2C_CLK_SRC_DEFAULT 0
#define I2C_ADDR_BIT_LEN_7 7
typedef struct {
  int i2c_port;
  int sda_io_num;
  int scl_io_num;
  int clk_source;
  int glitch_ignore_cnt;
  int intr_priority;
  int trans_queue_depth;
  struct { unsigned enable_internal_pullup : 1; } flags;
} i2c_master_bus_config_t;
typedef struct {
  int dev_addr_length;
  uint16_t device_address;
  int scl_speed_hz;
  int scl_wait_us;
  struct { unsigned disable_ack_check : 1; } flags;
} i2c_device_config_t;
esp_err_t i2c_new_master_bus(const i2c_master_bus_config_t *cfg, i2c_master_bus_handle_t *out);
esp_err_t i2c_del_master_bus(i2c_master_bus_handle_t bus);
esp_err_t i2c_master_probe(i2c_master_bus_handle_t bus, uint16_t addr, int timeout_ms);
esp_err_t i2c_master_bus_add_device(i2c_master_bus_handle_t bus, const i2c_device_config_t *cfg, i2c_master_dev_handle_t *out);
esp_err_t i2c_master_bus_rm_device(i2c_master_dev_handle_t dev);
esp_err_t i2c_master_transmit(i2c_master_dev_handle_t dev, const uint8_t *buf, size_t len, int timeout_ms);
esp_err_t i2c_master_transmit_receive(i2c_master_dev_handle_t dev, const uint8_t *tx, size_t txlen, uint8_t *rx, size_t rxlen, int timeout_ms);
""",
}

HARNESS = r"""
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "i2c_bus.h"
#include "driver/gpio.h"
#include "driver/i2c_master.h"
#include "freertos/semphr.h"

typedef struct { unsigned addr; int alive; } device_t;
static device_t devices[128];
static int add_count[128], remove_count[128];
static int bus_new_count, bus_delete_count, busy, fail_remove_addr = -1;
static int fail_add_addr = -1, mutex_create_count;
static int64_t clock_us = 0;
static int fake_bus, fake_mutex;

const char *esp_err_to_name(esp_err_t err) { (void)err; return "mock"; }
void esp_log_level_set(const char *tag, int level) { (void)tag; (void)level; }
void esp_rom_delay_us(unsigned delay) { (void)delay; }
int64_t esp_timer_get_time(void) { clock_us += 100; return clock_us; }
int gpio_set_direction(int pin, int mode) { (void)pin; (void)mode; return 0; }
int gpio_get_level(int pin) { (void)pin; return 1; }
int gpio_config(const gpio_config_t *cfg) { (void)cfg; return 0; }
int gpio_set_level(int pin, int level) { (void)pin; (void)level; return 0; }

SemaphoreHandle_t xSemaphoreCreateMutex(void) {
  mutex_create_count++;
  return &fake_mutex;
}
int xSemaphoreTake(SemaphoreHandle_t mutex, TickType_t timeout) {
  (void)timeout;
  assert(mutex == &fake_mutex);
  if (busy) return pdFALSE;
  busy = 1;
  return pdTRUE;
}
int xSemaphoreGive(SemaphoreHandle_t mutex) {
  assert(mutex == &fake_mutex && busy);
  busy = 0;
  return pdTRUE;
}
void vSemaphoreDelete(SemaphoreHandle_t mutex) { assert(mutex == &fake_mutex); }

esp_err_t i2c_new_master_bus(const i2c_master_bus_config_t *cfg, i2c_master_bus_handle_t *out) {
  assert(cfg->sda_io_num == 1 && cfg->scl_io_num == 2);
  assert(!busy || busy == 1);
  bus_new_count++;
  *out = &fake_bus;
  return ESP_OK;
}
esp_err_t i2c_del_master_bus(i2c_master_bus_handle_t bus) {
  assert(bus == &fake_bus);
  for (int i = 0; i < 128; i++) assert(!devices[i].alive);
  bus_delete_count++;
  return ESP_OK;
}
esp_err_t i2c_master_probe(i2c_master_bus_handle_t bus, uint16_t addr, int timeout_ms) {
  assert(bus == &fake_bus && timeout_ms > 0 && addr >= 0x03 && addr <= 0x77);
  return ESP_OK;
}
esp_err_t i2c_master_bus_add_device(i2c_master_bus_handle_t bus, const i2c_device_config_t *cfg, i2c_master_dev_handle_t *out) {
  assert(bus == &fake_bus && busy && cfg->dev_addr_length == I2C_ADDR_BIT_LEN_7);
  unsigned addr = cfg->device_address;
  assert(addr >= 0x03 && addr <= 0x77 && !devices[addr].alive);
  if ((int)addr == fail_add_addr) return ESP_FAIL;
  devices[addr] = (device_t){.addr = addr, .alive = 1};
  add_count[addr]++;
  *out = &devices[addr];
  return ESP_OK;
}
esp_err_t i2c_master_bus_rm_device(i2c_master_dev_handle_t handle) {
  device_t *dev = handle;
  assert(busy && dev->alive);
  if ((int)dev->addr == fail_remove_addr) return ESP_FAIL;
  remove_count[dev->addr]++;
  dev->alive = 0;
  return ESP_OK;
}
esp_err_t i2c_master_transmit(i2c_master_dev_handle_t handle, const uint8_t *buf, size_t len, int timeout_ms) {
  device_t *dev = handle;
  assert(busy && dev->alive && buf && len && timeout_ms > 0);
  return ESP_OK;
}
esp_err_t i2c_master_transmit_receive(i2c_master_dev_handle_t handle, const uint8_t *tx, size_t txlen, uint8_t *rx, size_t rxlen, int timeout_ms) {
  device_t *dev = handle;
  assert(busy && dev->alive && tx && txlen == 1 && rx && rxlen && timeout_ms > 0);
  memset(rx, 0x42, rxlen);
  return ESP_OK;
}

int main(void) {
  uint8_t result = 0, payload = 0x11;
  assert(i2c_bus_read(0x68, 0, &result, 1) == ESP_ERR_INVALID_STATE);
  assert(i2c_bus_write(0, 0, &payload, 1) == ESP_ERR_INVALID_ARG);
  assert(i2c_bus_probe_addr(0x78) == ESP_ERR_INVALID_ARG);

  assert(i2c_bus_init() == ESP_OK);
  assert(i2c_bus_init() == ESP_OK && bus_new_count == 1);
  fail_add_addr = 0x68;
  assert(i2c_bus_read(0x68, 0, &result, 1) == ESP_FAIL);
  assert(add_count[0x68] == 0);
  fail_add_addr = -1;
  assert(i2c_bus_read(0x68, 0, &result, 1) == ESP_OK && result == 0x42);
  for (int i = 0; i < 512; i++) {
    assert(i2c_bus_read(0x68, 0, &result, 1) == ESP_OK);
    assert(i2c_bus_write(0x68, 0, &payload, 1) == ESP_OK);
  }
  assert(add_count[0x68] == 1 && remove_count[0x68] == 0);
  assert(i2c_bus_read(0x69, 0, &result, 1) == ESP_OK);
  assert(add_count[0x69] == 1 && remove_count[0x69] == 0);
  assert(i2c_bus_scan() == ESP_OK);
  assert(i2c_bus_probe_addr(0x68) == ESP_OK);
  assert(i2c_bus_read(0x79, 0, &result, 1) == ESP_ERR_INVALID_ARG);

  fail_remove_addr = 0x68;
  i2c_bus_deinit();
  assert(bus_delete_count == 0 && devices[0x68].alive);
  fail_remove_addr = -1;
  i2c_bus_deinit();
  assert(bus_delete_count == 1 && remove_count[0x68] == 1 && remove_count[0x69] == 1);
  assert(i2c_bus_read(0x68, 0, &result, 1) == ESP_ERR_INVALID_STATE);
  assert(i2c_bus_init() == ESP_OK && bus_new_count == 2);
  assert(i2c_bus_read(0x68, 0, &result, 1) == ESP_OK && add_count[0x68] == 2);
  i2c_bus_deinit();
  assert(bus_delete_count == 2 && remove_count[0x68] == 2);
  assert(mutex_create_count == 1 && !busy);
  puts("I2C_DEVICE_CACHE_MOCK=PASS");
  return 0;
}
"""

class I2CBusHandleTests(unittest.TestCase):
  def test_compiles_and_reuses_devices_without_transfer_churn(self) -> None:
    compiler = shutil.which("cc") or shutil.which("gcc")
    if compiler is None:
      self.skipTest("C compiler unavailable")

    with tempfile.TemporaryDirectory(prefix="i2c-cache-") as temporary:
      work = Path(temporary)
      for name, contents in HEADERS.items():
        path = work / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents.strip() + "\n", encoding="utf-8")

      harness = work / "harness.c"
      harness.write_text(HARNESS, encoding="utf-8")
      executable = work / "i2c-test"
      command = [
        compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
        "-Wno-unused-variable", "-Wno-unused-parameter", "-Wno-unused-function",
        "-I", str(work), "-I", str(INCLUDE),
        str(SOURCE), str(harness), "-o", str(executable),
      ]
      compile_result = subprocess.run(command, capture_output=True, text=True, check=False)
      self.assertEqual(0, compile_result.returncode, compile_result.stderr)
      result = subprocess.run([str(executable)], capture_output=True, text=True, check=False)
      self.assertEqual(0, result.returncode, result.stderr)
      self.assertIn("I2C_DEVICE_CACHE_MOCK=PASS", result.stdout)


if __name__ == "__main__":
  unittest.main()
