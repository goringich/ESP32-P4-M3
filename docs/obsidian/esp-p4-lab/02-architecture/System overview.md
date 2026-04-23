# System overview

Прошивка состоит из нескольких слоев:

- `main`: минимальная точка входа ESP-IDF.
- `app`: прикладной координатор.
- `app_wifi`: Wi-Fi bringup и status.
- `app_net`: HTTP/WebSocket API.
- `app_stepper`: управление L293D stepper и UART.
- `app_mpu_pretty`: чтение и форматирование телеметрии MPU.
- `i2c_bus`: низкоуровневый I2C wrapper.
- `mpu9250`: минимальная логика обнаружения MPU и чтения WHO_AM_I.

Главная архитектурная идея после изменений:

- старое UART-управление не удалено;
- сетевое управление добавлено рядом;
- оба канала вызывают один и тот же command handler для stepper;
- сетевой слой читает snapshot, а не лезет напрямую во внутреннее состояние stepper;
- Wi-Fi может работать как точка доступа и как клиент.

См. [[02-architecture/UART and network dual control]] и [[02-architecture/WiFi HTTP WebSocket architecture]].

