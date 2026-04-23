# Boot and main loop

Стартовая цепочка:

1. ESP-IDF вызывает `app_main()` из `main/main.c`.
2. `app_main()` пишет лог `boot`.
3. `app_main()` вызывает `app_init()`.
4. `app_init()` поднимает подсистемы.
5. `app_main()` входит в бесконечный цикл.
6. На каждой итерации вызывается `app_tick()`.
7. Между итерациями выполняется `vTaskDelay(pdMS_TO_TICKS(app_tick_delay_ms()))`.

`app_init()` отвечает за разовый bringup:

- логирование;
- I2C init;
- I2C scan;
- MPU WHO_AM_I check;
- Wi-Fi bringup;
- stepper init;
- HTTP/WebSocket server start.

`app_tick()` отвечает за периодическую работу:

- stepper tick;
- WebSocket push tick;
- MPU/system telemetry, если включен `CONFIG_APP_TICK_LOG`.

См. [[04-functions/app_main]], [[04-functions/app_init]], [[04-functions/app_tick]].

