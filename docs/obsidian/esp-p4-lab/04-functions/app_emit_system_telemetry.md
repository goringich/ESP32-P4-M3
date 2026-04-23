# app_emit_system_telemetry

Исходник: `components/app/src/app.c`.

`app_emit_system_telemetry()` печатает системную telemetry строку.

Поля:

- `kind: system`;
- `uptime_ms`;
- `tick`;
- `tick_delay_ms`;
- `firmware`;
- `app_mode`.

Функция используется из `app_tick()` при включенном `CONFIG_APP_TICK_LOG`.

Это UART/log telemetry, не HTTP API.

