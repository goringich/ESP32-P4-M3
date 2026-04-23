# app_net_wifi_handler

Исходник: `components/app/src/app_net.c`.

`app_net_wifi_handler()` обрабатывает `GET /api/wifi`.

Что делает:

- получает `app_wifi_status_t` через `app_wifi_get_status()`;
- вручную собирает JSON только про Wi-Fi;
- если `snprintf` вернул ошибку, отправляет `HTTPD_500_INTERNAL_SERVER_ERROR`;
- выставляет CORS headers;
- выставляет `application/json`;
- отправляет JSON.

Используется для проверки сети без чтения stepper telemetry.

