# app_stepper_log_timing

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_log_timing()` печатает текущую задержку шага и скорость в шагах в секунду.

Используется после команд:

- `+`;
- `=`;
- `-`;
- `_`.

После лога вызывает `app_stepper_emit_telemetry(reason)`.

