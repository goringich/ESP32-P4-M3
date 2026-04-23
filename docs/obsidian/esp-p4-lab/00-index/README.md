# ESP P4 Lab Documentation

Это входная точка Obsidian-графа по прошивке `p4_lab`.

Цель графа: объяснить проект человеку, который немного понимает программирование, но не обязан заранее знать ESP-IDF, FreeRTOS, I2C, Wi-Fi SoftAP, HTTP server или управление шаговым двигателем через L293D.

Основной путь чтения:

- [[00-index/Reading order]]
- [[00-index/Function index]]
- [[00-index/Config index]]
- [[02-architecture/System overview]]
- [[02-architecture/Boot and main loop]]
- [[02-architecture/Runtime data flow]]
- [[02-architecture/WiFi HTTP WebSocket architecture]]
- [[02-architecture/UART and network dual control]]
- [[03-components/app component]]
- [[03-components/app_wifi]]
- [[03-components/app_net]]
- [[03-components/app_stepper]]
- [[03-components/i2c_bus]]
- [[03-components/mpu9250]]
- [[05-config/Configuration overview]]
- [[06-operations/Build and verification]]

Главные исходники:

- `main/main.c`
- `components/app/src/app.c`
- `components/app/src/app_wifi.c`
- `components/app/src/app_net.c`
- `components/app/src/app_stepper.c`
- `components/app/src/app_mpu_pretty.c`
- `components/i2c_bus/src/i2c_bus.c`
- `components/i2c_bus/src/i2c_bus_diag.c`
- `components/mpu9250/src/mpu9250.c`
- `components/app/Kconfig`
- `components/i2c_bus/Kconfig`
- `sdkconfig`
- `sdkconfig.defaults`

Что не документируется здесь:

- `stepper-remote/backend`
- `stepper-remote/frontend`
- внешний SDK `esp-idf`
- временный `build`
