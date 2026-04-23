# app_stepper_get_snapshot

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_get_snapshot()` копирует внутреннее состояние stepper в публичную структуру `app_stepper_snapshot_t`.

Что копируется:

- mode;
- sweep_state;
- step_delay_ms;
- steps_per_second;
- phase_index;
- total_steps;
- sweep_steps;
- coils_enabled;
- uart_ready;
- last_command;
- GPIO для IN1..IN4;
- LED GPIO или `-1`, если LED выключен.

Зачем это нужно:

- `app_net.c` может строить JSON без знания внутренних enum и state struct;
- публичный API остается узким;
- можно менять внутреннее устройство stepper, не переписывая сетевой слой.

