# app_wifi_smoke_run

Исходник: `components/app/src/app_wifi.c`.

`app_wifi_smoke_run()` сейчас фактически является Wi-Fi bringup-функцией, хотя имя осталось от старого smoke test.

Что делает:

- проверяет, включен ли Wi-Fi stack (`CONFIG_ESP_WIFI_ENABLED` или `CONFIG_ESP_HOST_WIFI_ENABLED`);
- не запускается повторно, если `s_wifi_started == true`;
- инициализирует NVS через `app_wifi_nvs_init_once()`;
- вызывает `esp_netif_init()`;
- создает default event loop через `esp_event_loop_create_default()`;
- создает STA netif через `esp_netif_create_default_wifi_sta()`;
- создает AP netif через `esp_netif_create_default_wifi_ap()`;
- инициализирует Wi-Fi через `esp_wifi_init()`;
- регистрирует common event handler;
- ставит `WIFI_MODE_APSTA`;
- строит AP SSID через `app_wifi_build_ap_ssid()`;
- конфигурирует SoftAP;
- при `CONFIG_APP_WIFI_CONNECT` конфигурирует STA;
- запускает Wi-Fi через `esp_wifi_start()`;
- отключает power save через `esp_wifi_set_ps(WIFI_PS_NONE)`;
- обновляет status;
- печатает STA MAC и AP info;
- выполняет scan через `app_wifi_log_scan_results()`;
- помечает `s_status.initialized = true` и `s_wifi_started = true`.

Ключевой результат: ESP поднимает точку доступа и готовит HTTP/WebSocket слой к запуску.

Связи:

- [[03-components/app_wifi]]
- [[04-functions/app_wifi_nvs_init_once]]
- [[04-functions/app_wifi_build_ap_ssid]]
- [[04-functions/app_wifi_log_scan_results]]
- [[04-functions/app_net_start]]

