# WiFi HTTP WebSocket architecture

Сетевая архитектура состоит из двух частей:

- `app_wifi.c`: поднимает Wi-Fi, создает AP/STA interfaces, хранит status.
- `app_net.c`: поднимает HTTP server и WebSocket endpoint.

Порядок работы:

1. `app_init()` вызывает `app_wifi_smoke_run()`.
2. Wi-Fi инициализирует NVS, netif, event loop.
3. Создаются STA и AP netif.
4. Выставляется `WIFI_MODE_APSTA`.
5. Конфигурируется SoftAP.
6. Если включен `CONFIG_APP_WIFI_CONNECT`, конфигурируется STA.
7. Запускается `esp_wifi_start()`.
8. `app_init()` устанавливает `s_network_ready = true`.
9. Если включен `CONFIG_APP_NET_ENABLE`, запускается `app_net_start()`.
10. HTTP server начинает принимать запросы.
11. `app_tick()` вызывает `app_net_tick()` для WebSocket broadcast.

Почему `APSTA`, а не только `STA`:

- без роутера можно подключиться к AP самой ESP;
- при наличии роутера можно подключить ESP в общую сеть;
- API не зависит от UART.

См. [[03-components/app_wifi]], [[03-components/app_net]].

