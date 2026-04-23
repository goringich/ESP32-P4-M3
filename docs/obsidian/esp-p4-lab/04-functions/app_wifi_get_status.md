# app_wifi_get_status

Исходник: `components/app/src/app_wifi.c`.

`app_wifi_get_status()` копирует текущее состояние Wi-Fi в структуру `app_wifi_status_t`.

Что находится в status:

- `initialized`: Wi-Fi bringup завершился;
- `ap_started`: SoftAP поднят;
- `sta_attempted`: STA-подключение пытались запустить;
- `sta_connected`: STA получила соединение;
- `ap_ssid`: SSID точки доступа ESP;
- `ap_ip`: IP адрес AP-интерфейса;
- `sta_ip`: IP адрес STA-интерфейса;
- `last_error`: последняя Wi-Fi ошибка.

Особенность реализации:

- сначала копирует `s_status`;
- затем вызывает `app_wifi_refresh_status_locked()`;
- затем явно обновляет поля в `status`.

Функция используется сетевым API в `app_net_build_json()` и `app_net_wifi_handler()`.

