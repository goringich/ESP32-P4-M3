# app_net

Файл: `components/app/src/app_net.c`.

Назначение:

- поднять HTTP server;
- зарегистрировать REST endpoints;
- зарегистрировать WebSocket endpoint;
- принимать сетевые команды управления stepper;
- отдавать телеметрию stepper и Wi-Fi;
- раз в секунду отправлять WebSocket broadcast клиентам.

Endpoints:

- `GET /api/telemetry`
- `GET /api/wifi`
- `POST /api/command`
- `OPTIONS /*`
- `GET /ws`

Главное состояние:

- `s_server`: handle HTTP server.
- `s_last_push_ms`: timestamp последней WebSocket рассылки.

Главные функции:

- [[04-functions/app_net_start]]
- [[04-functions/app_net_tick]]
- [[04-functions/app_net_build_json]]
- [[04-functions/app_net_command_handler]]
- [[04-functions/app_net_ws_handler]]

