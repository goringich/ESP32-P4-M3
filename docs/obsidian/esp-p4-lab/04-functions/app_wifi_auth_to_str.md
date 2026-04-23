# app_wifi_auth_to_str

Исходник: `components/app/src/app_wifi.c`.

`app_wifi_auth_to_str()` переводит `wifi_auth_mode_t` в короткую строку.

Примеры:

- `WIFI_AUTH_OPEN` -> `OPEN`;
- `WIFI_AUTH_WPA2_PSK` -> `WPA2-PSK`;
- `WIFI_AUTH_WPA3_PSK` -> `WPA3-PSK`;
- неизвестное значение -> `UNKNOWN`.

Используется при печати результатов Wi-Fi scan.

