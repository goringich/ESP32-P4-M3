# app_stepper

Файл: `components/app/src/app_stepper.c`.

Назначение:

- настроить GPIO для L293D;
- настроить UART0 для старого управления;
- хранить состояние двигателя;
- выполнять команды движения;
- управлять фазами;
- печатать статус и телеметрию;
- дать сетевому слою публичный API `app_stepper_command_char()` и `app_stepper_get_snapshot()`.

Главное состояние:

- `s_phases`: таблица фаз.
- `s_stepper`: текущий режим, фаза, задержка, счетчики, флаги UART/coils.

Режимы:

- `stop`
- `forward`
- `reverse`
- `sweep`

Главные функции:

- [[04-functions/app_stepper_init]]
- [[04-functions/app_stepper_tick]]
- [[04-functions/app_stepper_handle_command]]
- [[04-functions/app_stepper_command_char]]
- [[04-functions/app_stepper_get_snapshot]]
- [[04-functions/app_stepper_apply_phase]]
- [[04-functions/app_stepper_release]]

