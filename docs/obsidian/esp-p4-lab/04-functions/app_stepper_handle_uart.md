# app_stepper_handle_uart

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_handle_uart()` читает входящие байты из UART0.

Что делает:

- создает буфер `uint8_t buf[16]`;
- вызывает `uart_read_bytes(APP_STEPPER_UART_PORT, buf, sizeof(buf), 0)`;
- если байтов нет, выходит;
- для каждого прочитанного байта вызывает `app_stepper_handle_command(buf[i])`.

Таймаут чтения равен `0`, поэтому функция не блокирует главный цикл.

