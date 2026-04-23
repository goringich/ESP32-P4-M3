# app_stepper_apply_named_phase

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_apply_named_phase()` удерживает конкретную фазу `A`, `B`, `C` или `D`.

Что делает:

- проверяет, что индекс фазы допустим;
- переводит stepper в режим `stop`;
- записывает `phase_index`;
- применяет выбранную фазу;
- логирует уровни IN1..IN4;
- печатает telemetry `hold_phase`.

Используется командами:

- `a`
- `b`
- `c`
- `d`

