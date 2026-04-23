# app_wifi_event_handler_common

Исходник: `components/app/src/app_wifi.c`.

`app_wifi_event_handler_common()` принимает Wi-Fi и IP события от ESP-IDF.

Обрабатываемые события:

- `WIFI_EVENT_AP_START`: выставляет `s_status.ap_started = true`, обновляет IP status.
- `WIFI_EVENT_AP_STOP`: выставляет `s_status.ap_started = false`.
- `IP_EVENT_AP_STAIPASSIGNED`: обновляет IP status, когда клиенту AP выдан IP.

Если включен `CONFIG_APP_WIFI_CONNECT`, функция передает события в `app_wifi_event_handler()`, который занимается STA connect/retry/GOT_IP.

Зачем это нужно:

- Wi-Fi события приходят асинхронно;
- статус нельзя полностью узнать только в момент `esp_wifi_start()`;
- HTTP `/api/wifi` должен видеть обновленную картину.

