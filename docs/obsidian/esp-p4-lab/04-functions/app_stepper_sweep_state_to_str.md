# app_stepper_sweep_state_to_str

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_sweep_state_to_str()` переводит состояние sweep state machine в строку.

Значения:

- `APP_STEPPER_SWEEP_FORWARD` -> `forward`;
- `APP_STEPPER_SWEEP_REVERSE` -> `reverse`;
- `APP_STEPPER_SWEEP_PAUSE_AFTER_FORWARD` -> `pause_after_forward`;
- `APP_STEPPER_SWEEP_PAUSE_AFTER_REVERSE` -> `pause_after_reverse`;
- default -> `unknown`.

Используется в telemetry и snapshot.

