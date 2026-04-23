# app_wifi_refresh_status_locked

Исходник: `components/app/src/app_wifi.c`.

`app_wifi_refresh_status_locked()` обновляет IP-адреса в `s_status`.

Что делает:

- если `s_sta_netif` существует, вызывает `esp_netif_get_ip_info()` и пишет `sta_ip`;
- если `s_ap_netif` существует, вызывает `esp_netif_get_ip_info()` и пишет `ap_ip`;
- форматирует IP через `IPSTR` и `IP2STR`.

Слово `locked` в имени сейчас скорее намерение, чем реальная блокировка: mutex здесь не используется.

