# Source map

Карта исходников проекта:

- `main/main.c`: точка входа ESP-IDF, вызывает `app_init()`, затем бесконечно вызывает `app_tick()`.
- `components/app/src/app.c`: центральный координатор приложения.
- `components/app/src/app_wifi.c`: инициализация Wi-Fi, SoftAP, STA, scan, статус Wi-Fi.
- `components/app/src/app_net.c`: HTTP и WebSocket API поверх Wi-Fi.
- `components/app/src/app_stepper.c`: логика L293D, шаговый двигатель, UART-команды, сетевые команды через общий handler.
- `components/app/src/app_mpu_pretty.c`: красивый лог и телеметрия MPU.
- `components/i2c_bus/src/i2c_bus.c`: базовый I2C bus wrapper.
- `components/i2c_bus/src/i2c_bus_diag.c`: диагностический перебор пар SDA/SCL.
- `components/mpu9250/src/mpu9250.c`: минимальный driver-like wrapper для MPU9250/вариантов.

Публичные заголовки:

- `components/app/include/app.h`: публичный API главного app layer.
- `components/app/include/app_wifi.h`: публичный API Wi-Fi status/bringup.
- `components/app/include/app_net.h`: публичный API HTTP/WebSocket server.
- `components/app/include/app_stepper.h`: публичный API stepper и snapshot для сети.
- `components/app/include/app_mpu_pretty.h`: публичный API MPU logging.
- `components/i2c_bus/include/i2c_bus.h`: публичный API I2C.
- `components/i2c_bus/include/i2c_bus_diag.h`: публичный API I2C diagnostics.
- `components/mpu9250/include/mpu9250.h`: публичный API MPU probe/WHO_AM_I.

