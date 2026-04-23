# app_stepper_led_set

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_led_set()` выставляет activity LED в конкретное состояние.

Если `CONFIG_APP_STEPPER_LED_ENABLE` включен:

- `on == true` -> GPIO level `1`;
- `on == false` -> GPIO level `0`.

Если LED выключен в конфиге, аргумент гасится через `(void)on`.

