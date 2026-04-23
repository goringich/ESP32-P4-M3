# Current network configuration

Текущее состояние сети из `sdkconfig`:

```text
CONFIG_ESP_HOST_WIFI_ENABLED=y
CONFIG_HTTPD_WS_SUPPORT=y
CONFIG_APP_WIFI_SMOKE=y
CONFIG_APP_WIFI_AP_SSID_PREFIX="JC-ESP32P4M3"
CONFIG_APP_WIFI_AP_PASSWORD="esp32p4m3"
CONFIG_APP_WIFI_AP_CHANNEL=1
CONFIG_APP_WIFI_SCAN_MAX_AP=20
# CONFIG_APP_WIFI_CONNECT is not set
CONFIG_APP_NET_ENABLE=y
```

Смысл:

- ESP32-P4 использует host Wi-Fi path;
- WebSocket support включен;
- SoftAP поднимается на boot;
- HTTP/WebSocket API включен;
- подключение к роутеру пока выключено;
- direct connect к ESP через ее AP должен быть основным способом проверки без UART.

