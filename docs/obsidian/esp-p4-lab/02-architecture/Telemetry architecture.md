# Telemetry architecture

В проекте есть несколько форм телеметрии:

- printf lines с префиксом `@telemetry`;
- HTTP JSON ответ;
- WebSocket JSON broadcast.

`app_stepper_emit_telemetry()` печатает строку для UART/log потока.

`app_net_build_json()` собирает JSON для web API:

- берет snapshot stepper через `app_stepper_get_snapshot()`;
- берет Wi-Fi status через `app_wifi_get_status()`;
- кодирует поля в один JSON.

`app_net_tick()` раз в секунду рассылает этот JSON всем WebSocket-клиентам.

Важно: JSON собирается через `snprintf`, а не через JSON-библиотеку. Это просто и достаточно для фиксированной структуры, но требует аккуратности, если в будущем появятся строки от пользователя.

