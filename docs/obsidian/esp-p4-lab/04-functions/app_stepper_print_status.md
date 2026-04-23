# app_stepper_print_status

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_print_status()` печатает состояние stepper.

Поля:

- mode;
- delay;
- steps/s;
- phase;
- total_steps;
- coils;
- sweep_steps;
- uart state.

После text log вызывает `app_stepper_emit_telemetry("status")`.

