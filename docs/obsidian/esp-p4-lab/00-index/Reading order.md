# Reading order

Рекомендуемый порядок чтения:

1. [[01-concepts/ESP-IDF basics]]
2. [[01-concepts/FreeRTOS loop model]]
3. [[01-concepts/ESP error handling]]
4. [[02-architecture/System overview]]
5. [[02-architecture/Boot and main loop]]
6. [[02-architecture/Runtime data flow]]
7. [[02-architecture/WiFi HTTP WebSocket architecture]]
8. [[02-architecture/UART and network dual control]]
9. [[03-components/app component]]
10. [[03-components/app_wifi]]
11. [[03-components/app_net]]
12. [[03-components/app_stepper]]
13. [[03-components/i2c_bus]]
14. [[03-components/mpu9250]]
15. [[05-config/Configuration overview]]
16. [[06-operations/Build and verification]]

После обзорного чтения можно использовать:

- [[00-index/Function index]]
- [[00-index/Config index]]

Если нужно быстро понять только Wi-Fi и веб-управление, читай:

- [[02-architecture/WiFi HTTP WebSocket architecture]]
- [[03-components/app_wifi]]
- [[03-components/app_net]]
- [[04-functions/app_wifi_smoke_run]]
- [[04-functions/app_net_start]]
- [[04-functions/app_net_tick]]

Если нужно быстро понять мотор и старое UART-управление, читай:

- [[02-architecture/UART and network dual control]]
- [[03-components/app_stepper]]
- [[04-functions/app_stepper_init]]
- [[04-functions/app_stepper_tick]]
- [[04-functions/app_stepper_handle_command]]
