# app_net

Файл: `components/app/src/app_net.c`.

## Назначение компонента

`app_net` — сетевой фасад bench-прошивки. Он публикует состояние системы и передает команды в motor subsystem через публичный API, не управляя GPIO напрямую.

## Архитектурная граница

Сетевой task не должен сам менять motor state. `app_stepper_command_char()` ставит команду в FreeRTOS queue, а реальная обработка и GPIO mutation выполняются из app tick. Snapshot чтения синхронизирован отдельно.

Так transport не становится вторым владельцем исполнительного механизма.

## Endpoints

### `GET /`, `GET /pad`

Встроенный UI, обслуживаемый самой платой. Он является основным browser-клиентом embedded API и работает same-origin.

### `GET /api/status`

Компактный JSON со сводным system/Wi-Fi/stepper state.

### `GET /api/telemetry`

Полный JSON-объект, включающий:

- `system`;
- `mpu`;
- `i2c`;
- `stepper`;
- `wifi`;
- `ble`.

### `GET /api/wifi`

Отдельный Wi-Fi status.

### `POST /api/command`

Принимает только `application/json` и однобуквенное поле `command`:

```json
{"command":"f"}
```

Raw text body больше не является API-контрактом.

Если browser присылает `Origin`, он должен совпадать с текущим ESP HTTP host. Server-to-server клиент без browser Origin остается допустимым.

После валидации вызывается `app_stepper_command_char(cmd)`, который ставит команду в motor queue. Ошибка queue/full/init возвращается transport-слою.

### `GET /ws`

WebSocket endpoint:

- browser handshake проверяет same-origin;
- входящая команда использует JSON-формат;
- после сообщения возвращается актуальный JSON snapshot;
- `app_net_tick()` дополнительно делает периодический push.

## Почему wildcard CORS удалён

API умеет управлять физическим actuator. `Access-Control-Allow-Origin: *` позволял внешнему browser-origin обращаться к device API и не был нужен текущей архитектуре:

- встроенный UI same-origin;
- локальный Stepper Remote backend проксирует ESP server-to-server;
- server-to-server HTTP не использует browser CORS.

Поэтому embedded API теперь intentionally same-origin для browser traffic.

## Как формируется JSON

`app_net_build_json()` получает данные через публичные status/snapshot API:

- `app_stepper_get_snapshot()`;
- `app_wifi_get_status()`;
- `app_get_system_status()`;
- `app_mpu_get_status()`;
- `app_get_i2c_status()`;
- `app_get_ble_status()`.

Сетевой слой не читает private state других компонентов напрямую.

## WebSocket push

Раз в секунду `app_net_tick()`:

1. проверяет server handle;
2. ограничивает cadence через `s_last_push_ms`;
3. получает список клиентов;
4. выбирает WebSocket clients;
5. строит JSON;
6. ставит отправку через `httpd_queue_work()`.

## Fail-soft startup

`app_net_start()` не использует fatal `ESP_ERROR_CHECK` для регистрации URI. Если один из handlers не зарегистрирован:

- ошибка логируется;
- HTTP server останавливается;
- `s_server` сбрасывается;
- ошибка возвращается в `app_init()`;
- остальные embedded-подсистемы продолжают жить.

## Ограничения

- нет пользовательской authentication/authorization;
- нет TLS;
- JSON собирается вручную;
- HTTP API относится к legacy bench infrastructure, а не к release spherical-robot controller;
- удаленное управление всё равно требует доверенной сети/операторского контура.

См. также:

- [[04-functions/app_net_start]]
- [[04-functions/app_net_tick]]
- [[04-functions/app_net_build_json]]
- [[04-functions/app_net_command_handler]]
- [[04-functions/app_net_ws_handler]]
- [[02-architecture/WiFi HTTP WebSocket architecture]]
