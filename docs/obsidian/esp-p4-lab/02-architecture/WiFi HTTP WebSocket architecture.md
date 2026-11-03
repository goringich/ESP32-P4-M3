# WiFi HTTP WebSocket architecture

## Слои

Сетевая архитектура разделена на:

- `app_wifi.c` — radio/network bring-up и Wi-Fi status;
- `app_net.c` — HTTP/WebSocket application transport.

Motor GPIO/state не принадлежит network task: внешние команды сериализуются через stepper queue и исполняются из app tick.

## Startup

1. `app_init()` поднимает локальные подсистемы.
2. `app_wifi_smoke_run()` инициализирует network stack и SoftAP/STA.
3. При успешной сети `app_net_start()` запускает HTTP server.
4. URI registration выполняется fail-soft: ошибка API setup не reset-ит MCU.
5. `app_tick()` вызывает `app_net_tick()` только если API успешно стартовал.

В tracked defaults STA auto-connect выключен; private STA credentials не являются частью repository config.

## API

- `GET /`, `GET /pad` — embedded same-origin UI;
- `GET /api/status` — compact status;
- `GET /api/telemetry` — full telemetry;
- `GET /api/wifi` — Wi-Fi state;
- `POST /api/command` — `application/json` command;
- `GET /ws` — WebSocket push/command channel.

## Browser security boundary

Embedded actuator API больше не публикует wildcard CORS.

Для browser-origin traffic:

- HTTP commands требуют current-host origin;
- WebSocket handshake проверяет Origin;
- cross-origin browser control не является поддерживаемым контрактом.

Это не заменяет полноценную authentication/TLS, но убирает ненужный wildcard browser access.

Локальный Stepper Remote backend при необходимости обращается к ESP server-to-server, поэтому browser CORS ему не нужен.

## Pull и push

REST/status endpoints дают pull-модель.

`app_net_tick()` раз в секунду:

- получает active sockets;
- выбирает WebSocket clients;
- строит единый JSON;
- ставит async send через `httpd_queue_work()`.

## State composition

Network layer собирает state через публичные APIs:

- `app_stepper_get_snapshot()`;
- `app_wifi_get_status()`;
- `app_get_system_status()`;
- `app_mpu_get_status()`;
- `app_get_i2c_status()`;
- `app_get_ble_status()`.

## Ограничения

- нет end-user auth;
- нет TLS;
- JSON manual `snprintf`;
- текущая network/control часть относится к bench infrastructure;
- product spherical controller должен иметь отдельный hardware/control safety contract.

См. также:

- [[03-components/app_wifi]]
- [[03-components/app_net]]
- [[06-operations/Runtime WiFi verification without UART]]
- [[06-operations/API examples]]
