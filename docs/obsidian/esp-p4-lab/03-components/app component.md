# app component

`components/app` - главный прикладной компонент.

Он содержит:

- центральный координатор `app.c`;
- Wi-Fi bringup `app_wifi.c`;
- HTTP/WebSocket API `app_net.c`;
- stepper control `app_stepper.c`;
- MPU pretty telemetry `app_mpu_pretty.c`;
- публичные заголовки в `include`.

Главная роль компонента:

- скрыть детали ESP-IDF от `main`;
- собрать все подсистемы в один жизненный цикл;
- дать проекту единый `app_init()`, `app_tick()`, `app_tick_delay_ms()`.

См. [[04-functions/app_init]], [[04-functions/app_tick]].

