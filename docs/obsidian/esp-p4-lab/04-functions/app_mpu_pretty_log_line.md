# app_mpu_pretty_log_line

Исходник: `components/app/src/app_mpu_pretty.c`.

`app_mpu_pretty_log_line()` читает сырые данные MPU и печатает человекочитаемую строку.

Что делает:

- вычисляет uptime;
- вызывает `app_mpu_pretty_init()`;
- при ошибке печатает MPU error telemetry;
- читает 14 байт начиная с `MPU_REG_ACCEL_XOUT_H`;
- разбирает accelerometer, temperature, gyroscope;
- переводит raw accel в `g`;
- переводит raw gyro в `dps`;
- переводит raw temperature в Celsius;
- печатает строку;
- вызывает `app_mpu_emit_telemetry_ready()`.

Сырые 14 байт идут в порядке:

- accel X/Y/Z;
- temperature;
- gyro X/Y/Z.

