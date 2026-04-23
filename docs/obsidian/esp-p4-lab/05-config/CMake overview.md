# CMake overview

ESP-IDF использует CMake, но компоненты объявляются через `idf_component_register`.

Корневой `CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.16)
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(p4_lab)
```

`main/CMakeLists.txt` регистрирует `main.c`.

`components/app/CMakeLists.txt` регистрирует прикладные C-файлы и зависимости:

- `i2c_bus`;
- `mpu9250`;
- `esp_driver_gpio`;
- `esp_driver_uart`;
- `esp_wifi`;
- `esp_event`;
- `esp_http_server`;
- `esp_netif`;
- `nvs_flash`.

`components/i2c_bus/CMakeLists.txt` регистрирует I2C sources и private dependencies.

`components/mpu9250/CMakeLists.txt` регистрирует MPU source и зависит от `i2c_bus`.

