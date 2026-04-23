# sdkconfig

Файл: `sdkconfig`.

`sdkconfig` - сгенерированное состояние конфигурации ESP-IDF. Его обычно не редактируют руками, но он важен для понимания текущей сборки.

Важные текущие значения:

- target: `CONFIG_IDF_TARGET="esp32p4"`;
- Wi-Fi для ESP32-P4 через host Wi-Fi: `CONFIG_ESP_HOST_WIFI_ENABLED=y`;
- WebSocket support: `CONFIG_HTTPD_WS_SUPPORT=y`;
- console UART: `CONFIG_ESP_CONSOLE_UART_DEFAULT=y`;
- LWIP sockets: `CONFIG_LWIP_MAX_SOCKETS=10`;
- app mode: `CONFIG_APP_MODE_L293D_TEST=y`;
- Wi-Fi bringup: `CONFIG_APP_WIFI_SMOKE=y`;
- HTTP/WebSocket API: `CONFIG_APP_NET_ENABLE=y`;
- SoftAP SSID prefix: `CONFIG_APP_WIFI_AP_SSID_PREFIX="JC-ESP32P4M3"`;
- SoftAP password: `CONFIG_APP_WIFI_AP_PASSWORD="esp32p4m3"`;
- SoftAP channel: `CONFIG_APP_WIFI_AP_CHANNEL=1`;
- STA connect: `# CONFIG_APP_WIFI_CONNECT is not set`.

Если нужно подключать ESP к домашнему Wi-Fi как STA, включи `APP_WIFI_CONNECT` и задай SSID/password через `idf.py menuconfig`.

