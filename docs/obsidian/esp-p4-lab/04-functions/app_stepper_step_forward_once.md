# app_stepper_step_forward_once

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_step_forward_once()` делает один шаг вперед.

Алгоритм:

- считает количество фаз;
- применяет текущую фазу `s_phases[s_stepper.phase_index]`;
- увеличивает `phase_index`;
- если индекс дошел до конца, возвращает его в `0`;
- увеличивает `total_steps`.

Движение получается за счет последовательного прохода по фазам вперед.

