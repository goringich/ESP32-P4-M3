# Runtime WiFi verification without UART

Проверка без UART означает: не читать serial monitor, а проверять устройство по сети.

Шаги:

1. Прошить ESP.
2. Подождать boot.
3. Найти Wi-Fi сеть с префиксом `JC-ESP32P4M3`.
4. Подключиться к ней паролем `esp32p4m3`.
5. Открыть `http://192.168.4.1/api/wifi`.
6. Открыть `http://192.168.4.1/api/telemetry`.
7. Отправить команду через `POST /api/command`.
8. Проверить WebSocket `/ws` из веб-приложения.

Ожидаемые признаки:

- `/api/wifi` возвращает `ok: true`;
- `apStarted` равен `true`;
- `apSsid` начинается с `JC-ESP32P4M3`;
- `/api/telemetry` содержит `stepper` и `wifi`;
- команда `s` переводит stepper в `stop`;
- команда `w` включает sweep;
- WebSocket раз в секунду получает JSON.

