idf_component_register(
  SRCS "src/i2c_bus.c" "src/i2c_bus_diag.c"
  INCLUDE_DIRS "include"
  PRIV_REQUIRES driver esp_timer
)
