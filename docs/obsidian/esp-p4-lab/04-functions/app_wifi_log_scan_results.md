# app_wifi_log_scan_results

Исходник: `components/app/src/app_wifi.c`.

`app_wifi_log_scan_results()` выполняет Wi-Fi scan и печатает найденные точки доступа.

Что делает:

- выделяет массив `wifi_ap_record_t` через `calloc`;
- запускает scan через `esp_wifi_scan_start(&scan_cfg, true)`;
- забирает результаты через `esp_wifi_scan_get_ap_records()`;
- печатает количество найденных AP;
- для каждой AP печатает SSID, RSSI, channel и тип auth;
- освобождает память через `free(records)`.

Зачем функция нужна:

- проверить, что Wi-Fi radio реально видит эфир;
- диагностировать антенну, канал, страну, питание;
- увидеть, находится ли рядом нужная сеть для STA mode.

Риск:

- scan блокирующий, потому что второй аргумент `esp_wifi_scan_start` равен `true`;
- это нормально на boot, но не стоит часто делать в runtime loop.

