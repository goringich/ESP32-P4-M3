# Configuration overview

Главные файлы конфигурации:

- `components/app/Kconfig`
- `components/i2c_bus/Kconfig`
- `sdkconfig`
- `sdkconfig.defaults`
- `CMakeLists.txt`

`Kconfig` описывает опции, которые можно менять через `idf.py menuconfig`.

`sdkconfig` хранит выбранные значения для текущей сборки.

`sdkconfig.defaults` задает baseline значения, которые применяются при создании нового `sdkconfig`.

Главные включенные опции сейчас:

- `CONFIG_IDF_TARGET="esp32p4"`
- `CONFIG_ESP_HOST_WIFI_ENABLED=y`
- `CONFIG_HTTPD_WS_SUPPORT=y`
- `CONFIG_APP_MODE_L293D_TEST=y`
- `CONFIG_APP_WIFI_SMOKE=y`
- `CONFIG_APP_NET_ENABLE=y`
- `CONFIG_APP_WIFI_AP_SSID_PREFIX="JC-ESP32P4M3"`
- `CONFIG_APP_WIFI_AP_PASSWORD="esp32p4m3"`
- `CONFIG_APP_WIFI_AP_CHANNEL=1`
- `# CONFIG_APP_WIFI_CONNECT is not set`

