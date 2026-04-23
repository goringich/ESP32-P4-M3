# app_stepper_mode_to_str

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_mode_to_str()` переводит enum режима stepper в строку.

Значения:

- `APP_STEPPER_MODE_STOP` -> `stop`;
- `APP_STEPPER_MODE_FORWARD` -> `forward`;
- `APP_STEPPER_MODE_REVERSE` -> `reverse`;
- `APP_STEPPER_MODE_SWEEP` -> `sweep`;
- default -> `unknown`.

Используется в логах, UART telemetry и HTTP/WebSocket snapshot.

