# app_wifi_smoke_run

Исходник: `components/app/src/app_wifi.c`.

## Назначение

`app_wifi_smoke_run()` по смыслу уже является не просто smoke-test, а основной функцией Wi‑Fi bringup. Имя историческое, а роль — вполне центральная.

Именно она подготавливает сетевую среду для будущего HTTP/WebSocket API.

## Что делает функция

- проверяет, включен ли Wi‑Fi stack (`CONFIG_ESP_WIFI_ENABLED` или `CONFIG_ESP_HOST_WIFI_ENABLED`);
- не запускается повторно, если `s_wifi_started == true`;
- инициализирует NVS через `app_wifi_nvs_init_once()`;
- вызывает `esp_netif_init()`;
- создает default event loop через `esp_event_loop_create_default()`;
- создает STA netif через `esp_netif_create_default_wifi_sta()`;
- создает AP netif через `esp_netif_create_default_wifi_ap()`;
- инициализирует Wi‑Fi через `esp_wifi_init()`;
- регистрирует common event handler;
- выбирает режим Wi‑Fi через `app_wifi_pick_mode()`;
- строит AP SSID через `app_wifi_build_ap_ssid()`;
- конфигурирует SoftAP;
- при `CONFIG_APP_WIFI_CONNECT` и непустом SSID конфигурирует STA;
- запускает Wi‑Fi через `esp_wifi_start()`;
- отключает power save через `esp_wifi_set_ps(WIFI_PS_NONE)`;
- обновляет status;
- помечает `s_status.initialized = true` и `s_wifi_started = true`.

## Важная точность по режиму работы

Функция **не всегда** ставит `WIFI_MODE_APSTA`.

Реальное поведение такое:

- если `CONFIG_APP_WIFI_CONNECT` выключен или SSID пустой, выбирается `WIFI_MODE_AP`;
- если STA-подключение включено и SSID задан, выбирается `WIFI_MODE_APSTA`.

Это важно, потому что текущая конфигурация проекта по умолчанию работает именно в AP-only режиме.

## Что функция сейчас НЕ делает

Несмотря на наличие соответствующего helper'а в коде, `app_wifi_smoke_run()` сейчас не вызывает `app_wifi_log_scan_results()` автоматически.

То есть:

- scan-функция существует;
- но список найденных точек доступа при старте автоматически не печатается.

## Ключевой результат

После успешного выполнения функция:

- поднимает сетевую среду;
- делает доступным SoftAP;
- при соответствующей конфигурации инициирует STA-подключение;
- готовит систему к запуску `app_net_start()`.

## Связи

- [[03-components/app_wifi]]
- [[04-functions/app_wifi_nvs_init_once]]
- [[04-functions/app_wifi_build_ap_ssid]]
- [[04-functions/app_net_start]]

