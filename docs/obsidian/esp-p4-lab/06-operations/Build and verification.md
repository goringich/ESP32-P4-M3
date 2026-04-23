# Build and verification

Последняя проверка сборки выполнялась отдельным build directory, чтобы не трогать мусорный tracked `build/` в репозитории:

```bash
export IDF_PATH="$HOME/esp/esp-idf"
source "$IDF_PATH/export.sh"
idf.py -B /tmp/esp_build build
```

Результат:

```text
Project build complete.
```

Что это подтверждает:

- C-файлы компилируются;
- новые `app_net.c` и `app_wifi.c` включены в сборку;
- `CONFIG_HTTPD_WS_SUPPORT=y` применен;
- зависимости `esp_http_server`, `esp_wifi`, `esp_netif`, `nvs_flash` найдены;
- UART-код не удален и собирается.

Что это не подтверждает:

- что плата реально успешно подключилась по Wi-Fi;
- что компьютер подключился к SoftAP;
- что HTTP endpoints отвечают на живом железе.

Для проверки без UART после прошивки:

```bash
curl http://192.168.4.1/api/wifi
curl http://192.168.4.1/api/telemetry
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"s"}'
```

