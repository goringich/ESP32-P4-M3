# API examples

Получить Wi-Fi status:

```bash
curl http://192.168.4.1/api/wifi
```

Получить общую телеметрию:

```bash
curl http://192.168.4.1/api/telemetry
```

Остановить мотор:

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"s"}'
```

Запустить вперед:

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"f"}'
```

Запустить sweep:

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"w"}'
```

Короткое тело тоже поддерживается:

```bash
curl -X POST http://192.168.4.1/api/command -d 's'
```

