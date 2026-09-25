# app_net_request_is_json

Исходник: `components/app/src/app_net.c`.

Проверяет, что `POST /api/command` использует `Content-Type: application/json`.

Raw single-character HTTP body больше не считается API-контрактом. Команда передается как:

```json
{"command":"f"}
```

Это делает transport contract явным и исключает простой cross-origin form-style command path.
