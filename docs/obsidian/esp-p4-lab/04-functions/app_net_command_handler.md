# app_net_command_handler

Исходник: `components/app/src/app_net.c`.

`app_net_command_handler()` обрабатывает `POST /api/command`.

Что делает:

- читает body через `httpd_req_recv()`;
- проверяет, что body не пустой;
- достает команду через `app_net_extract_command()`;
- вызывает `app_stepper_command_char(cmd)`;
- если команда обработана, возвращает обычный telemetry JSON через `app_net_telemetry_handler(req)`.

Пример запроса:

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"s"}'
```

Связи:

- [[04-functions/app_net_extract_command]]
- [[04-functions/app_stepper_command_char]]
- [[04-functions/app_net_telemetry_handler]]

