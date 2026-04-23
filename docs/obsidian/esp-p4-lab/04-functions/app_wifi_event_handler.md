# app_wifi_event_handler

Исходник: `components/app/src/app_wifi.c`.

`app_wifi_event_handler()` компилируется только если включен `CONFIG_APP_WIFI_CONNECT`.

Назначение:

- обработать STA start;
- вызвать `esp_wifi_connect()`;
- обработать STA disconnect;
- сделать retry до `APP_WIFI_MAX_RETRIES`;
- обработать `IP_EVENT_STA_GOT_IP`;
- записать `sta_connected` и `sta_ip`.

Если `CONFIG_APP_WIFI_SSID` пустой, функция не пытается подключаться.

Сейчас `CONFIG_APP_WIFI_CONNECT` выключен, поэтому этот код не участвует в текущей сборке.

