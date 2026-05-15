# API examples

## Назначение API

Сетевой API проекта нужен для двух вещей:

- читать текущее состояние прошивки;
- передавать команды управления шаговым двигателем.

В текущем виде API достаточно прост, чтобы его можно было использовать:

- вручную через `curl`;
- из web-приложения;
- из тестового скрипта;
- как источник примеров для описания в курсовой.

Базовый адрес при работе через SoftAP:

```text
http://192.168.4.1
```

## Получить Wi‑Fi status

```bash
curl http://192.168.4.1/api/wifi
```

Типичный смысл ответа:

- инициализирован ли Wi‑Fi;
- поднят ли SoftAP;
- пытался ли модуль подключаться как STA;
- какой IP сейчас у AP/STA.

## Получить общую телеметрию

```bash
curl http://192.168.4.1/api/telemetry
```

Это главный endpoint. Он возвращает сводное состояние по разделам:

- `system`
- `mpu`
- `i2c`
- `stepper`
- `wifi`

Именно этот endpoint удобнее всего использовать как основу для будущего web-dashboard.

## Команды управления двигателем

### Остановить мотор

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"s"}'
```

### Запустить вперед

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"f"}'
```

### Запустить назад

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"r"}'
```

### Включить режим sweep

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"w"}'
```

### Один шаг вперед

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"1"}'
```

### Один шаг назад

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"2"}'
```

### Ускорить

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"+"}'
```

### Замедлить

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"-"}'
```

### Освободить катушки

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"z"}'
```

## Упрощенный формат body

В текущем коде поддерживается не только JSON, но и короткое текстовое тело. Например:

```bash
curl -X POST http://192.168.4.1/api/command -d 's'
```

Это удобно для ручной проверки API и для минималистичных клиентов.

## Что возвращает `POST /api/command`

После успешного выполнения команда не просто отвечает `OK`, а возвращает актуальную телеметрию через тот же механизм, что и `GET /api/telemetry`.

Это удобно, потому что клиент сразу получает обновленное состояние системы после команды.

## WebSocket

Для постоянного соединения используется endpoint:

```text
ws://192.168.4.1/ws
```

Через него можно:

- отправлять те же команды;
- получать обновления состояния раз в секунду.

## Почему это полезно для курсовой

Этот раздел дает готовые практические примеры взаимодействия с embedded-устройством по сети. Их можно использовать:

- как примеры API-запросов;
- как основу для описания REST/WebSocket интерфейса;
- как доказательство прикладной ценности проекта.

