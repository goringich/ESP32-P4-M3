# app_net_set_cors

Исходник: `components/app/src/app_net.c`.

`app_net_set_cors()` выставляет CORS headers для HTTP response.

Headers:

- `Access-Control-Allow-Origin: *`;
- `Access-Control-Allow-Methods: GET,POST,OPTIONS`;
- `Access-Control-Allow-Headers: Content-Type`.

Это нужно, чтобы веб-приложение на компьютере могло делать запросы к ESP с другого origin.

