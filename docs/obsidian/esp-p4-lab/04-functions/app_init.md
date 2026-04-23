# app_init

Исходник: `components/app/src/app.c`.

`app_init()` - центральная функция разовой инициализации проекта.

Порядок действий:

- настраивает уровни логирования;
- печатает блок `APP INITIALIZATION`;
- вызывает `i2c_bus_init()`;
- вызывает `i2c_bus_scan()`;
- вызывает `app_mpu_whoami_check()`;
- если включен `CONFIG_APP_WIFI_SMOKE`, вызывает `app_wifi_smoke_run()`;
- если Wi-Fi успешно поднят, ставит `s_network_ready = true`;
- если включен `CONFIG_APP_MODE_L293D_TEST`, вызывает `app_stepper_init()`;
- если включен `CONFIG_APP_NET_ENABLE` и сеть готова, вызывает `app_net_start()`.

Важная деталь: сетевой сервер не стартует сам по себе. Он стартует только после успешного Wi-Fi bringup.

Связи:

- [[04-functions/i2c_bus_init]]
- [[04-functions/i2c_bus_scan]]
- [[04-functions/app_wifi_smoke_run]]
- [[04-functions/app_stepper_init]]
- [[04-functions/app_net_start]]

