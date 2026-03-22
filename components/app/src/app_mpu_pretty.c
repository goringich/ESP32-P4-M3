#include "app_mpu_pretty.h"

#include <inttypes.h>
#include <stdbool.h>
#include <stdio.h>

#include "esp_log.h"

#include "i2c_bus.h"
#include "mpu9250.h"

static const char *TAG = "app_mpu";

static const uint8_t MPU_REG_PWR_MGMT_1 = 0x6B;
static const uint8_t MPU_REG_GYRO_CONFIG = 0x1B;
static const uint8_t MPU_REG_ACCEL_CONFIG = 0x1C;
static const uint8_t MPU_REG_ACCEL_XOUT_H = 0x3B;

#define APP_MPU_COLOR_RESET "\x1b[0m"
#define APP_MPU_COLOR_HEADER "\x1b[38;5;178m"
#define APP_MPU_COLOR_ACCEL "\x1b[38;5;51m"
#define APP_MPU_COLOR_GYRO "\x1b[38;5;213m"
#define APP_MPU_COLOR_TEMP "\x1b[38;5;220m"
#define APP_MPU_COLOR_ERR "\x1b[1;31m"
#define APP_MPU_LINE_WIDTH 180

typedef struct {
  uint8_t addr;
  uint8_t whoami;
  float accel_lsb_per_g;
  float gyro_lsb_per_dps;
  bool ready;
} app_mpu_state_t;

static app_mpu_state_t s_mpu = {
  .addr = 0,
  .whoami = 0,
  .accel_lsb_per_g = 16384.0f,
  .gyro_lsb_per_dps = 131.0f,
  .ready = false,
};

static int16_t app_mpu_i16be(const uint8_t hi, const uint8_t lo);
static float app_mpu_accel_lsb_per_g(uint8_t accel_cfg);
static float app_mpu_gyro_lsb_per_dps(uint8_t gyro_cfg);
static void app_mpu_emit_telemetry_ready(uint32_t tick_counter,
                                         uint32_t uptime_min,
                                         uint32_t uptime_rem_sec,
                                         uint8_t who,
                                         float ax_g,
                                         float ay_g,
                                         float az_g,
                                         float gx_dps,
                                         float gy_dps,
                                         float gz_dps,
                                         float temp_c);
static void app_mpu_emit_telemetry_error(esp_err_t err);

static int16_t app_mpu_i16be(const uint8_t hi, const uint8_t lo) {
  return (int16_t)(((uint16_t)hi << 8) | lo);
}

static float app_mpu_accel_lsb_per_g(uint8_t accel_cfg) {
  const uint8_t afs_sel = (accel_cfg >> 3) & 0x03;
  switch (afs_sel) {
    case 0:
      return 16384.0f;  /* +/-2g */
    case 1:
      return 8192.0f;   /* +/-4g */
    case 2:
      return 4096.0f;   /* +/-8g */
    case 3:
      return 2048.0f;   /* +/-16g */
    default:
      return 16384.0f;
  }
}

static float app_mpu_gyro_lsb_per_dps(uint8_t gyro_cfg) {
  const uint8_t fs_sel = (gyro_cfg >> 3) & 0x03;
  switch (fs_sel) {
    case 0:
      return 131.0f;  /* +/-250 dps */
    case 1:
      return 65.5f;   /* +/-500 dps */
    case 2:
      return 32.8f;   /* +/-1000 dps */
    case 3:
      return 16.4f;   /* +/-2000 dps */
    default:
      return 131.0f;
  }
}

static void app_mpu_emit_telemetry_ready(uint32_t tick_counter,
                                         uint32_t uptime_min,
                                         uint32_t uptime_rem_sec,
                                         uint8_t who,
                                         float ax_g,
                                         float ay_g,
                                         float az_g,
                                         float gx_dps,
                                         float gy_dps,
                                         float gz_dps,
                                         float temp_c) {
  printf("@telemetry {\"kind\":\"mpu\",\"ready\":true,\"address\":\"0x%02X\",\"whoami\":\"0x%02X\","
         "\"model\":\"%s\",\"uptime\":\"%02" PRIu32 ":%02" PRIu32 "\","
         "\"tick\":%" PRIu32 ",\"accel\":{\"x_g\":%.3f,\"y_g\":%.3f,\"z_g\":%.3f},"
         "\"gyro\":{\"x_dps\":%.2f,\"y_dps\":%.2f,\"z_dps\":%.2f},\"temp_c\":%.2f}\n",
         s_mpu.addr,
         who,
         mpu9250_whoami_name(who),
         uptime_min,
         uptime_rem_sec,
         tick_counter,
         (double)ax_g,
         (double)ay_g,
         (double)az_g,
         (double)gx_dps,
         (double)gy_dps,
         (double)gz_dps,
         (double)temp_c);
}

static void app_mpu_emit_telemetry_error(esp_err_t err) {
  printf("@telemetry {\"kind\":\"mpu\",\"ready\":false,\"error\":\"%s\"}\n", esp_err_to_name(err));
}

esp_err_t app_mpu_pretty_init(void) {
  uint8_t who = 0;
  uint8_t pwr = 0;
  uint8_t gyro_cfg = 0;
  uint8_t accel_cfg = 0;

  if (s_mpu.ready) {
    return ESP_OK;
  }

  esp_err_t err = mpu9250_probe_and_read_whoami(&s_mpu.addr, &who);
  if (err != ESP_OK) {
    return err;
  }

  err = i2c_bus_write(s_mpu.addr, MPU_REG_PWR_MGMT_1, &pwr, 1);
  if (err != ESP_OK) {
    return err;
  }

  err = i2c_bus_read(s_mpu.addr, MPU_REG_GYRO_CONFIG, &gyro_cfg, 1);
  if (err != ESP_OK) {
    return err;
  }

  err = i2c_bus_read(s_mpu.addr, MPU_REG_ACCEL_CONFIG, &accel_cfg, 1);
  if (err != ESP_OK) {
    return err;
  }

  s_mpu.gyro_lsb_per_dps = app_mpu_gyro_lsb_per_dps(gyro_cfg);
  s_mpu.accel_lsb_per_g = app_mpu_accel_lsb_per_g(accel_cfg);
  s_mpu.whoami = who;
  s_mpu.ready = true;

  ESP_LOGI(TAG,
           "ready: addr=0x%02X who=0x%02X accel_lsb/g=%.1f gyro_lsb/dps=%.1f",
           s_mpu.addr,
           who,
           (double)s_mpu.accel_lsb_per_g,
           (double)s_mpu.gyro_lsb_per_dps);

  return ESP_OK;
}

esp_err_t app_mpu_pretty_log_line(uint32_t tick_counter, uint32_t uptime_ms) {
  uint8_t raw[14] = {0};
  char line[320];

  const uint32_t uptime_sec = uptime_ms / 1000U;
  const uint32_t uptime_min = uptime_sec / 60U;
  const uint32_t uptime_rem_sec = uptime_sec % 60U;

  esp_err_t err = app_mpu_pretty_init();
  if (err != ESP_OK) {
    snprintf(line,
             sizeof(line),
             "%sMPU ERR%s #%-6" PRIu32 " up %02" PRIu32 ":%02" PRIu32 " : %s",
             APP_MPU_COLOR_ERR,
             APP_MPU_COLOR_RESET,
             tick_counter,
             uptime_min,
             uptime_rem_sec,
             esp_err_to_name(err));

    printf("%s\n", line);
    app_mpu_emit_telemetry_error(err);
    fflush(stdout);
    return err;
  }

  err = i2c_bus_read(s_mpu.addr, MPU_REG_ACCEL_XOUT_H, raw, sizeof(raw));
  if (err != ESP_OK) {
    snprintf(line,
             sizeof(line),
             "%sMPU ERR%s #%-6" PRIu32 " up %02" PRIu32 ":%02" PRIu32 " : %s",
             APP_MPU_COLOR_ERR,
             APP_MPU_COLOR_RESET,
             tick_counter,
             uptime_min,
             uptime_rem_sec,
             esp_err_to_name(err));

    printf("%s\n", line);
    app_mpu_emit_telemetry_error(err);
    fflush(stdout);
    return err;
  }

  const int16_t ax_raw = app_mpu_i16be(raw[0], raw[1]);
  const int16_t ay_raw = app_mpu_i16be(raw[2], raw[3]);
  const int16_t az_raw = app_mpu_i16be(raw[4], raw[5]);
  const int16_t temp_raw = app_mpu_i16be(raw[6], raw[7]);
  const int16_t gx_raw = app_mpu_i16be(raw[8], raw[9]);
  const int16_t gy_raw = app_mpu_i16be(raw[10], raw[11]);
  const int16_t gz_raw = app_mpu_i16be(raw[12], raw[13]);

  const float ax_g = (float)ax_raw / s_mpu.accel_lsb_per_g;
  const float ay_g = (float)ay_raw / s_mpu.accel_lsb_per_g;
  const float az_g = (float)az_raw / s_mpu.accel_lsb_per_g;
  const float gx_dps = (float)gx_raw / s_mpu.gyro_lsb_per_dps;
  const float gy_dps = (float)gy_raw / s_mpu.gyro_lsb_per_dps;
  const float gz_dps = (float)gz_raw / s_mpu.gyro_lsb_per_dps;
  const float temp_c = ((float)temp_raw / 333.87f) + 21.0f;

  snprintf(line,
           sizeof(line),
           "%sMPU%s #%-6" PRIu32 " up %02" PRIu32 ":%02" PRIu32
           " | %sA[g]%s %+6.3f %+6.3f %+6.3f"
           " | %sG[dps]%s %+7.2f %+7.2f %+7.2f"
           " | %sT%s %+6.2fC",
           APP_MPU_COLOR_HEADER,
           APP_MPU_COLOR_RESET,
           tick_counter,
           uptime_min,
           uptime_rem_sec,
           APP_MPU_COLOR_ACCEL,
           APP_MPU_COLOR_RESET,
           (double)ax_g,
           (double)ay_g,
           (double)az_g,
           APP_MPU_COLOR_GYRO,
           APP_MPU_COLOR_RESET,
           (double)gx_dps,
           (double)gy_dps,
           (double)gz_dps,
           APP_MPU_COLOR_TEMP,
           APP_MPU_COLOR_RESET,
           (double)temp_c);

  printf("%s\n", line);
  app_mpu_emit_telemetry_ready(
    tick_counter,
    uptime_min,
    uptime_rem_sec,
    s_mpu.whoami,
    ax_g,
    ay_g,
    az_g,
    gx_dps,
    gy_dps,
    gz_dps,
    temp_c
  );
  fflush(stdout);

  return ESP_OK;
}
