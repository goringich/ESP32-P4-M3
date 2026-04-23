# Runtime data flow

Основные потоки данных:

- UART byte -> `app_stepper_handle_uart()` -> `app_stepper_handle_command()`.
- HTTP POST body -> `app_net_command_handler()` -> `app_stepper_command_char()` -> `app_stepper_handle_command()`.
- WebSocket text frame -> `app_net_ws_handler()` -> `app_stepper_command_char()` -> `app_stepper_handle_command()`.
- Stepper state -> `app_stepper_get_snapshot()` -> `app_net_build_json()` -> HTTP/WebSocket JSON.
- Wi-Fi state -> `app_wifi_get_status()` -> `app_net_build_json()` -> HTTP/WebSocket JSON.
- I2C bus -> `mpu9250_*` -> `app_mpu_pretty_*` -> UART/log telemetry text.

Это важная развязка:

- `app_net` не знает внутренних enum stepper;
- `app_net` не дергает GPIO напрямую;
- `app_wifi` не знает про мотор;
- `app_stepper` не знает про HTTP/WebSocket;
- `app.c` собирает подсистемы вместе.

