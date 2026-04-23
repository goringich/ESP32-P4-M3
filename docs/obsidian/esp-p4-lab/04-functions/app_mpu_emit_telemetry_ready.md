# app_mpu_emit_telemetry_ready

Исходник: `components/app/src/app_mpu_pretty.c`.

`app_mpu_emit_telemetry_ready()` печатает telemetry строку, когда MPU успешно прочитан.

Поля:

- `kind: mpu`;
- `ready: true`;
- `address`;
- `whoami`;
- `model`;
- `uptime`;
- `tick`;
- `accel.x_g/y_g/z_g`;
- `gyro.x_dps/y_dps/z_dps`;
- `temp_c`.

Эта telemetry идет в stdout/UART log, а не в HTTP API.

