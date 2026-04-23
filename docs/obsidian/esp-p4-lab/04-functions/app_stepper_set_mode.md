# app_stepper_set_mode

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_set_mode()` меняет режим движения.

Режимы:

- `APP_STEPPER_MODE_STOP`
- `APP_STEPPER_MODE_FORWARD`
- `APP_STEPPER_MODE_REVERSE`
- `APP_STEPPER_MODE_SWEEP`

Что делает:

- если режим уже такой же, ничего не меняет;
- обновляет `s_stepper.mode`;
- сбрасывает pause/tick счетчики;
- если новый режим `stop`, вызывает `app_stepper_release()`;
- если режим не `stop`, сбрасывает `last_step_ms`, чтобы следующий tick мог шагнуть сразу;
- печатает telemetry.

