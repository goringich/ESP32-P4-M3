# app_stepper_step_reverse_once

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_step_reverse_once()` делает один шаг назад.

Алгоритм:

- считает количество фаз;
- если `phase_index == 0`, переносит индекс на последнюю фазу;
- иначе уменьшает `phase_index`;
- применяет фазу;
- увеличивает `total_steps`.

Движение назад получается за счет прохода по той же таблице фаз в обратном направлении.

