# app_tick

Исходник: `components/app/src/app.c`.

`app_tick()` - периодическая функция приложения. Ее вызывает `app_main()` каждые `APP_MAIN_TICK_MS` миллисекунд.

Что делает:

- если включен L293D test mode, вызывает `app_stepper_tick()`;
- если включен network API, вызывает `app_net_tick()`;
- если включен `CONFIG_APP_TICK_LOG`, раз в секунду печатает system telemetry и MPU telemetry.

Почему функция устроена через `#if`:

- ESP-IDF config генерирует compile-time macros;
- ненужный код может быть исключен при сборке;
- один проект можно собирать в разных режимах.

Связи:

- [[04-functions/app_stepper_tick]]
- [[04-functions/app_net_tick]]
- [[04-functions/app_mpu_pretty_log_line]]

