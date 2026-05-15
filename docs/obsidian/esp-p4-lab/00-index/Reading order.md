# Reading order

Этот файл задает не просто список страниц, а несколько разных маршрутов чтения в зависимости от цели.

## Базовый маршрут: быстро понять весь проект

Если нужно получить цельную картину прошивки, лучше идти в таком порядке:

1. [[00-index/README]]
2. [[01-concepts/ESP-IDF basics]]
3. [[01-concepts/FreeRTOS loop model]]
4. [[01-concepts/ESP error handling]]
5. [[01-concepts/WiFi AP STA basics]]
6. [[01-concepts/HTTP and WebSocket basics]]
7. [[01-concepts/I2C basics]]
8. [[01-concepts/Stepper and L293D basics]]
9. [[02-architecture/System overview]]
10. [[02-architecture/Boot and main loop]]
11. [[02-architecture/Runtime data flow]]
12. [[02-architecture/WiFi HTTP WebSocket architecture]]
13. [[02-architecture/UART and network dual control]]
14. [[02-architecture/Telemetry architecture]]
15. [[03-components/app component]]
16. [[03-components/app_wifi]]
17. [[03-components/app_net]]
18. [[03-components/app_stepper]]
19. [[03-components/i2c_bus]]
20. [[03-components/mpu9250]]
21. [[05-config/Configuration overview]]
22. [[06-operations/Build and verification]]

Этот маршрут лучше всего подходит, если нужно потом писать связный обзор проекта для курсовой.

## Маршрут: только сеть и удаленное управление

Если задача — понять Wi‑Fi, HTTP, WebSocket и API, читай:

- [[02-architecture/WiFi HTTP WebSocket architecture]]
- [[02-architecture/UART and network dual control]]
- [[03-components/app_wifi]]
- [[03-components/app_net]]
- [[04-functions/app_wifi_smoke_run]]
- [[04-functions/app_net_start]]
- [[04-functions/app_net_build_json]]
- [[04-functions/app_net_tick]]
- [[06-operations/API examples]]
- [[06-operations/Runtime WiFi verification without UART]]

## Маршрут: только мотор и локальное управление

Если нужно быстро понять stepper и старое UART-управление:

- [[02-architecture/UART and network dual control]]
- [[03-components/app_stepper]]
- [[04-functions/app_stepper_init]]
- [[04-functions/app_stepper_tick]]
- [[04-functions/app_stepper_handle_command]]
- [[04-functions/app_stepper_get_snapshot]]

## Маршрут: только сенсорная часть и I2C

Если нужен MPU/I2C-путь:

- [[01-concepts/I2C basics]]
- [[03-components/i2c_bus]]
- [[03-components/mpu9250]]
- [[04-functions/i2c_bus_init]]
- [[04-functions/i2c_bus_scan]]
- [[04-functions/mpu9250_probe_and_read_whoami]]
- [[04-functions/app_mpu_pretty_init]]
- [[04-functions/app_mpu_pretty_log_line]]

## Когда использовать индексы

После обзорного чтения лучше переходить к индексам:

- [[00-index/Function index]] — если нужна навигация по поведению кода;
- [[00-index/Config index]] — если нужно понять, что задается конфигом;
- [[00-index/Source map]] — если нужно быстро найти физические файлы.

## Практический совет

Для подготовки курсовой лучше читать именно слоями:

1. концепции;
2. архитектура;
3. компоненты;
4. функции;
5. конфигурация;
6. эксплуатация и верификация.

Так текст потом сам собирается в правильную структуру главы. Почти как будто проект сам пишет пояснительную записку, если его достаточно долго читать. Почти.
