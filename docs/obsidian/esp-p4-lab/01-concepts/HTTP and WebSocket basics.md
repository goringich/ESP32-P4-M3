# HTTP and WebSocket basics

Проект использует две сетевые модели:

- HTTP request/response для точечных запросов;
- WebSocket для постоянного соединения и периодической телеметрии.

HTTP endpoints:

- `GET /api/telemetry`: возвращает общий JSON с состоянием stepper и Wi-Fi.
- `GET /api/wifi`: возвращает только Wi-Fi status.
- `POST /api/command`: принимает команду для stepper.
- `OPTIONS /*`: отвечает на CORS preflight.

WebSocket endpoint:

- `GET /ws`: WebSocket handshake;
- входящее текстовое сообщение может содержать команду;
- раз в секунду `app_net_tick()` рассылает telemetry JSON всем WebSocket-клиентам.

См. [[03-components/app_net]], [[04-functions/app_net_ws_handler]], [[04-functions/app_net_tick]].

