# app_stepper_apply_phase

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_apply_phase()` применяет одну фазу к GPIO входам L293D.

Что делает:

- выставляет IN1;
- выставляет IN2;
- выставляет IN3;
- выставляет IN4;
- ставит `s_stepper.coils_enabled = true`;
- переключает activity LED через `app_stepper_led_toggle()`.

Фаза передается как `app_stepper_phase_t`, где есть четыре логических уровня и label.

