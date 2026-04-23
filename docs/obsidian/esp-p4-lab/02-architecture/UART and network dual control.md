# UART and network dual control

Требование: не удалять старое UART-управление, но добавить Wi-Fi/HTTP/WebSocket.

Решение:

- UART остается внутри `app_stepper.c`.
- Сетевой слой не копирует command logic.
- Добавлена публичная функция `app_stepper_command_char(char cmd)`.
- UART и сеть сходятся в одном внутреннем handler: `app_stepper_handle_command(uint8_t cmd)`.

Путь UART:

```text
UART0 -> app_stepper_handle_uart -> app_stepper_handle_command
```

Путь HTTP:

```text
POST /api/command -> app_net_command_handler -> app_stepper_command_char -> app_stepper_handle_command
```

Путь WebSocket:

```text
/ws text frame -> app_net_ws_handler -> app_stepper_command_char -> app_stepper_handle_command
```

Так сохраняется совместимость: команды `f`, `r`, `s`, `w`, `1`, `2`, `a`, `b`, `c`, `d`, `+`, `-`, `z` одинаковы для UART и сети.

