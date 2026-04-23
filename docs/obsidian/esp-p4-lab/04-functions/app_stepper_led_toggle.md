# app_stepper_led_toggle

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_led_toggle()` переключает activity LED.

Что делает при включенном `CONFIG_APP_STEPPER_LED_ENABLE`:

- инвертирует `s_stepper.led_state`;
- пишет новый уровень в `CONFIG_APP_STEPPER_LED_GPIO`.

Вызывается при применении фазы, то есть LED может мигать на шагах двигателя.

