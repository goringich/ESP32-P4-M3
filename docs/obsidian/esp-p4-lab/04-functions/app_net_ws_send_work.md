# app_net_ws_send_work

Исходник: `components/app/src/app_net.c`.

`app_net_ws_send_work()` выполняет фактическую асинхронную отправку WebSocket frame.

Что делает:

- получает `app_net_ws_msg_t *`;
- создает `httpd_ws_frame_t`;
- выставляет `final = true`;
- выставляет `type = HTTPD_WS_TYPE_TEXT`;
- отправляет frame через `httpd_ws_send_frame_async()`;
- при ошибке пишет warning;
- освобождает `msg`.

Функция вызывается не напрямую из app loop, а через `httpd_queue_work()`.

