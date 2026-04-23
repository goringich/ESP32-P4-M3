# app_stepper_uart_init

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_uart_init()` поднимает старый UART control path.

Что делает:

- настраивает `UART_NUM_0`;
- ставит baud rate из `CONFIG_APP_STEPPER_UART_BAUD_RATE`;
- использует 8 data bits;
- отключает parity;
- использует 1 stop bit;
- отключает hardware flow control;
- устанавливает UART driver через `uart_driver_install()`;
- применяет параметры через `uart_param_config()`;
- ставит режим `UART_MODE_UART`;
- выставляет `s_stepper.uart_ready = true`.

Если `uart_driver_install()` возвращает `ESP_ERR_INVALID_STATE`, это не считается фатальной ошибкой: драйвер уже мог быть установлен.

