idf_component_register(
  SRCS "src/app.c" "src/app_mpu_pretty.c" "src/app_wifi.c"
  INCLUDE_DIRS "include"
  REQUIRES i2c_bus mpu9250 esp_wifi esp_event esp_netif nvs_flash
)
