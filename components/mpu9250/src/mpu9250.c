#include "mpu9250.h"

#include "i2c_bus.h"

static const uint8_t MPU_REG_PWR_MGMT_1 = 0x6B;
static const uint8_t MPU_REG_WHO_AM_I = 0x75;

esp_err_t mpu9250_probe_addr(uint8_t *out_addr) {
  if (out_addr == NULL) {
    return ESP_ERR_INVALID_ARG;
  }

  for (uint8_t addr = 0x68; addr <= 0x69; addr++) {
    esp_err_t err = i2c_bus_probe_addr(addr);
    if (err == ESP_OK) {
      *out_addr = addr;
      return ESP_OK;
    }
  }

  return ESP_ERR_NOT_FOUND;
}

esp_err_t mpu9250_read_whoami(uint8_t addr, uint8_t *out_whoami) {
  if (out_whoami == NULL) {
    return ESP_ERR_INVALID_ARG;
  }

  uint8_t pwr = 0x00;
  (void)i2c_bus_write(addr, MPU_REG_PWR_MGMT_1, &pwr, 1);

  return i2c_bus_read(addr, MPU_REG_WHO_AM_I, out_whoami, 1);
}

esp_err_t mpu9250_probe_and_read_whoami(uint8_t *out_addr, uint8_t *out_whoami) {
  if (out_addr == NULL || out_whoami == NULL) {
    return ESP_ERR_INVALID_ARG;
  }

  esp_err_t err = mpu9250_probe_addr(out_addr);
  if (err != ESP_OK) {
    return err;
  }

  return mpu9250_read_whoami(*out_addr, out_whoami);
}

const char *mpu9250_whoami_name(uint8_t whoami) {
  switch (whoami) {
    case 0x70:
      return "MPU-6500";
    case 0x71:
      return "MPU-9250";
    case 0x73:
      return "MPU-9255/variant";
    default:
      return "unknown/clone";
  }
}
