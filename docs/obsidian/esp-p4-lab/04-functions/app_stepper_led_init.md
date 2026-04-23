# app_stepper_led_init

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_led_init()` компилирует полезное тело только если включен `CONFIG_APP_STEPPER_LED_ENABLE`.

Что делает при включенном LED:

- настраивает `CONFIG_APP_STEPPER_LED_GPIO` как output;
- выставляет уровень `0`.

Если LED выключен в конфиге, функция фактически пустая.

