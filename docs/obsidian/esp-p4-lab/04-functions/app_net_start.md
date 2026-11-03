# app_net_start

Исходник: `components/app/src/app_net.c`.

`app_net_start()` запускает HTTP/WebSocket API поверх уже поднятой сетевой среды.

## Startup contract

1. Если `s_server != NULL`, функция возвращает `ESP_OK`.
2. Создается `HTTPD_DEFAULT_CONFIG()`.
3. Запускается `httpd_start()`.
4. Последовательно регистрируются URI handlers.
5. Если любая регистрация не проходит, ошибка логируется, server останавливается, `s_server` сбрасывается и ошибка возвращается вызывающему коду.

Здесь намеренно нет fatal `ESP_ERROR_CHECK()`: сетевой API не должен reset-ить весь MCU из-за локальной ошибки HTTP setup.

## Endpoints

- `GET /` — встроенный UI;
- `GET /pad` — тот же compact operator UI route;
- `GET /api/status` — status snapshot;
- `GET /api/telemetry` — полная телеметрия;
- `GET /api/wifi` — Wi-Fi status;
- `POST /api/command` — same-origin JSON command;
- `GET /ws` — WebSocket telemetry/command endpoint.

Wildcard CORS и `OPTIONS /*` удалены. Browser control является same-origin; внешний Node bridge работает server-to-server.

## Архитектурный смысл

Wi-Fi bring-up и API startup остаются разными слоями:

`app_init -> app_wifi_smoke_run -> app_net_start`

Если API не поднялся, network status/error остается наблюдаемым, но firmware может продолжить локальную работу.

См. также:

- [[04-functions/app_net_tick]]
- [[04-functions/app_net_build_json]]
- [[02-architecture/WiFi HTTP WebSocket architecture]]
