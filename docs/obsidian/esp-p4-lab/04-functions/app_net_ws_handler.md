# app_net_ws_handler

Исходник: `components/app/src/app_net.c`.

`app_net_ws_handler()` обслуживает WebSocket endpoint `/ws`.

Поведение при `HTTP_GET`:

- это handshake;
- логирует подключение;
- возвращает `ESP_OK`.

Поведение при WebSocket frame:

- сначала вызывает `httpd_ws_recv_frame(req, &frame, 0)`, чтобы узнать длину;
- выделяет payload буфер через `calloc`;
- читает frame целиком;
- если frame текстовый и непустой, пытается достать команду;
- если команда найдена, вызывает `app_stepper_command_char(cmd)`;
- освобождает payload;
- строит свежий JSON;
- отправляет JSON как WebSocket text frame.

Отдельно `app_net_tick()` позже рассылает heartbeat telemetry всем WebSocket-клиентам.

