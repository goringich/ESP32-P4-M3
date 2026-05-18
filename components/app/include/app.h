#pragma once

#include <stdbool.h>
#include <stdint.h>

void app_init(void);
void app_tick(void);
unsigned int app_tick_delay_ms(void);

typedef struct {
  bool ready;
  uint32_t uptime_ms;
  uint32_t tick;
  uint32_t tick_delay_ms;
  char firmware[32];
  char app_mode[32];
  char last_error[32];
} app_system_status_t;

typedef struct {
  bool ready;
  uint8_t device_count;
  char devices[2][8];
  char detected_mpu_address[8];
  char last_scan_summary[48];
  char error[32];
} app_i2c_status_t;

typedef struct {
  bool initialized;
  bool controller_enabled;
  bool advertising;
  bool connected;
  bool notify_enabled;
  char device_name[32];
  char address[24];
  char last_error[32];
} app_ble_status_t;

void app_get_system_status(app_system_status_t *status);
void app_get_i2c_status(app_i2c_status_t *status);
void app_get_ble_status(app_ble_status_t *status);
void app_set_system_error(const char *error);
