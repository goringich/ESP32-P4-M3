idf_component_register(
  SRCS "src/app.c"
  INCLUDE_DIRS "include"
  REQUIRES i2c_bus mpu9250
)
