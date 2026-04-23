# Header files

Публичные header files задают границы между компонентами.

`app.h`:

- `app_init()`;
- `app_tick()`;
- `app_tick_delay_ms()`.

`app_wifi.h`:

- `app_wifi_status_t`;
- `app_wifi_smoke_run()`;
- `app_wifi_get_status()`.

`app_net.h`:

- `app_net_start()`;
- `app_net_tick()`.

`app_stepper.h`:

- `app_stepper_snapshot_t`;
- `app_stepper_init()`;
- `app_stepper_tick()`;
- `app_stepper_command_char()`;
- `app_stepper_get_snapshot()`.

`i2c_bus.h`:

- init/deinit/scan/probe/read/write.

`mpu9250.h`:

- probe/read WHO_AM_I helper API.

