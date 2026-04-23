# app_wifi

Файл: `components/app/src/app_wifi.c`.

Назначение:

- инициализировать Wi-Fi stack;
- создать STA и AP сетевые интерфейсы;
- запустить `WIFI_MODE_APSTA`;
- создать SoftAP с SSID на базе MAC-суффикса;
- при включенном `CONFIG_APP_WIFI_CONNECT` попытаться подключиться к роутеру;
- выполнить scan доступных точек;
- хранить и отдавать status через `app_wifi_get_status()`.

Ключевое состояние:

- `s_sta_netif`: указатель на STA netif.
- `s_ap_netif`: указатель на AP netif.
- `s_wifi_started`: флаг, что Wi-Fi уже стартовал.
- `s_status`: публично отдаваемое состояние Wi-Fi.

Главные функции:

- [[04-functions/app_wifi_smoke_run]]
- [[04-functions/app_wifi_get_status]]
- [[04-functions/app_wifi_event_handler_common]]
- [[04-functions/app_wifi_log_scan_results]]
- [[04-functions/app_wifi_build_ap_ssid]]
- [[04-functions/app_wifi_nvs_init_once]]

