# app_stepper_print_help

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_print_help()` печатает список команд stepper.

Команды включают:

- help/status;
- stop/forward/reverse/sweep;
- single-step forward/reverse;
- hold phase A/B/C/D;
- speed up / slow down;
- release coils.

Это справка для UART пользователя, но команды совпадают с network API.

