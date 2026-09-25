# app_net_set_common_headers

Исходник: `components/app/src/app_net.c`.

Функция выставляет только response cache-control headers:

- `Cache-Control: no-store, no-cache, must-revalidate, max-age=0`;
- `Pragma: no-cache`;
- `Expires: 0`.

Она намеренно не включает `Access-Control-Allow-Origin`.

Browser API на ESP является same-origin. Это важно, потому что `POST /api/command` управляет physical bench actuator.
