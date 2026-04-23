# Component dependency graph

Компоненты ESP-IDF:

```text
main
  -> app

app
  -> i2c_bus
  -> mpu9250
  -> esp_driver_gpio
  -> esp_driver_uart
  -> esp_wifi
  -> esp_event
  -> esp_http_server
  -> esp_netif
  -> nvs_flash

mpu9250
  -> i2c_bus

i2c_bus
  -> driver
  -> esp_timer
```

Эта структура задается в:

- `components/app/CMakeLists.txt`
- `components/i2c_bus/CMakeLists.txt`
- `components/mpu9250/CMakeLists.txt`
- `main/CMakeLists.txt`

См. [[05-config/CMake overview]].

