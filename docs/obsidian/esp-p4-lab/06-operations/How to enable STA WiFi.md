# How to enable STA WiFi

Сейчас SoftAP включен, а подключение к роутеру как STA выключено:

```text
# CONFIG_APP_WIFI_CONNECT is not set
```

Чтобы ESP подключалась к существующей Wi-Fi сети:

```bash
idf.py menuconfig
```

Дальше:

- зайти в `app`;
- включить `attempt Wi-Fi connect after scan`;
- задать `Wi-Fi SSID`;
- задать `Wi-Fi password`;
- сохранить конфиг;
- собрать и прошить.

После этого `app_wifi_smoke_run()`:

- оставит SoftAP включенным;
- настроит STA credentials;
- при `WIFI_EVENT_STA_START` вызовет `esp_wifi_connect()`;
- при disconnect будет делать retry;
- при `IP_EVENT_STA_GOT_IP` заполнит `sta_ip`.

См. [[04-functions/app_wifi_event_handler_common]].

