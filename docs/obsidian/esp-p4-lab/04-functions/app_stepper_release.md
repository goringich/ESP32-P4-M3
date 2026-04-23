# app_stepper_release

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_release()` отпускает обмотки двигателя.

Что делает:

- выставляет все IN1..IN4 в `0`;
- ставит `s_stepper.coils_enabled = false`;
- сбрасывает `s_stepper.led_state = false`;
- выключает LED через `app_stepper_led_set(false)`.

Это важно для:

- режима `stop`;
- пауз sweep на краях;
- команды `z`;
- безопасного начального состояния после init.

