# app_wifi_build_ap_ssid

Исходник: `components/app/src/app_wifi.c`.

`app_wifi_build_ap_ssid()` собирает имя точки доступа ESP.

Формат:

```text
CONFIG_APP_WIFI_AP_SSID_PREFIX-<MAC bytes 3..5>
```

Пример:

```text
JC-ESP32P4M3-A1B2C3
```

Почему добавляется MAC-суффикс:

- если рядом несколько плат, SSID не будут полностью одинаковыми;
- пользователь может отличить свою плату;
- префикс остается читаемым.

Если MAC не передан, функция просто копирует `CONFIG_APP_WIFI_AP_SSID_PREFIX`.

