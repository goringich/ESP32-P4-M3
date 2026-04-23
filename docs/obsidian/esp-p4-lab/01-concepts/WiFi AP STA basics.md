# WiFi AP STA basics

Wi-Fi в проекте поднят в режиме `WIFI_MODE_APSTA`.

Это комбинированный режим:

- `AP`: ESP создает свою точку доступа, к которой может подключиться компьютер или телефон.
- `STA`: ESP сама может подключаться к существующему роутеру как клиент.

Зачем это нужно:

- без роутера можно подключиться напрямую к ESP через ее AP;
- при наличии роутера ESP может быть участником общей сети;
- HTTP и WebSocket API доступны поверх Wi-Fi, а UART остается резервным локальным каналом.

Точка доступа настраивается через:

- `CONFIG_APP_WIFI_AP_SSID_PREFIX`
- `CONFIG_APP_WIFI_AP_PASSWORD`
- `CONFIG_APP_WIFI_AP_CHANNEL`

STA-подключение включается отдельно через:

- `CONFIG_APP_WIFI_CONNECT`
- `CONFIG_APP_WIFI_SSID`
- `CONFIG_APP_WIFI_PASSWORD`

См. [[03-components/app_wifi]].

