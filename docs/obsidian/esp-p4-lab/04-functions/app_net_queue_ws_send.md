# app_net_queue_ws_send

Исходник: `components/app/src/app_net.c`.

`app_net_queue_ws_send()` ставит асинхронную отправку WebSocket frame в очередь HTTP server.

Что делает:

- проверяет, что server и payload существуют;
- выделяет `app_net_ws_msg_t`;
- сохраняет server handle, socket fd и payload;
- вызывает `httpd_queue_work(s_server, app_net_ws_send_work, msg)`;
- если поставить задачу в очередь не удалось, освобождает память.

Зачем нужна отдельная структура `app_net_ws_msg_t`:

- async work выполнится позже;
- payload должен жить дольше, чем stack frame текущей функции;
- поэтому данные копируются в heap object.

