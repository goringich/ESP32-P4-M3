# HTTP and WebSocket basics

Проект использует две сетевые модели:

- HTTP request/response для точечных запросов;
- WebSocket для постоянного соединения и периодической телеметрии.

HTTP endpoints:

- `GET /` и `GET /pad`: встроенный same-origin UI;
- `GET /api/status`: компактный status snapshot;
- `GET /api/telemetry`: полный JSON состояния;
- `GET /api/wifi`: Wi-Fi status;
- `POST /api/command`: same-origin JSON-команда для bench stepper.

Команда по HTTP принимается только как `application/json`:

```json
{"command":"f"}
```

Wildcard CORS и `OPTIONS /*` больше не используются. Встроенный UI работает с API на том же origin, а внешний Node bridge обращается к ESP server-to-server, поэтому CORS ему не нужен.

WebSocket endpoint:

- `GET /ws`: WebSocket handshake;
- browser handshake с `Origin` принимается только для origin текущего ESP HTTP host;
- текстовая команда использует тот же JSON-формат;
- раз в секунду `app_net_tick()` рассылает telemetry JSON всем WebSocket-клиентам.

Это safety boundary: случайный внешний web-origin не должен получать прямой browser-control над actuator API.

См. [[03-components/app_net]], [[04-functions/app_net_ws_handler]], [[04-functions/app_net_tick]].
