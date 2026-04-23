# app_net_telemetry_handler

Исходник: `components/app/src/app_net.c`.

`app_net_telemetry_handler()` обрабатывает `GET /api/telemetry`.

Что делает:

- выделяет stack buffer `json`;
- вызывает `app_net_build_json()`;
- выставляет CORS headers через `app_net_set_cors()`;
- выставляет response type `application/json`;
- отправляет строку через `httpd_resp_sendstr()`.

Эта функция также используется после успешной команды в `POST /api/command`, чтобы клиент сразу получил новое состояние.

