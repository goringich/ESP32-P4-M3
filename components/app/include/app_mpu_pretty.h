#pragma once

#include <stdbool.h>
#include <stdint.h>

#include "esp_err.h"

typedef struct {
  bool ready;
  char error[32];
  char address[8];
  char whoami[8];
  char model[24];
  char uptime[8];
  float accel_x_g;
  float accel_y_g;
  float accel_z_g;
  float gyro_x_dps;
  float gyro_y_dps;
  float gyro_z_dps;
  float temp_c;
} app_mpu_status_t;

esp_err_t app_mpu_pretty_init(void);
esp_err_t app_mpu_pretty_log_line(uint32_t tick_counter, uint32_t uptime_ms);
void app_mpu_get_status(app_mpu_status_t *status);

/* Fast IMU read for the control loop — no logging, no telemetry. */
esp_err_t app_mpu_read_fast(float *ax_g, float *ay_g, float *az_g,
                             float *gx_dps, float *gy_dps, float *gz_dps);
