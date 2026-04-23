# app_net_start

Исходник: `components/app/src/app_net.c`.

`app_net_start()` запускает HTTP/WebSocket server.

Что делает:

- если `s_server != NULL`, возвращает `ESP_OK`;
- создает `httpd_config_t config = HTTPD_DEFAULT_CONFIG()`;
- выставляет `config.max_uri_handlers = 8`;
- вызывает `httpd_start(&s_server, &config)`;
- регистрирует URI handlers:
- `GET /api/telemetry`;
- `GET /api/wifi`;
- `POST /api/command`;
- `OPTIONS /*`;
- `GET /ws` как WebSocket.

Важно:

- функция вызывается из `app_init()` только если Wi-Fi успешно поднялся;
- WebSocket поддержка требует `CONFIG_HTTPD_WS_SUPPORT=y`;
- при ошибке старта возвращает ошибку, и network API не используется.

Связи:

- [[04-functions/app_net_telemetry_handler]]
- [[04-functions/app_net_wifi_handler]]
- [[04-functions/app_net_command_handler]]
- [[04-functions/app_net_ws_handler]]

