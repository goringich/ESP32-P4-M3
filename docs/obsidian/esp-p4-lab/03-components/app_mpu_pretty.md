# app_mpu_pretty

Файл: `components/app/src/app_mpu_pretty.c`.

Назначение:

- обнаружить MPU;
- вывести WHO_AM_I;
- прочитать конфиги gyro/accel scale;
- периодически читать 14 байт raw telemetry;
- перевести raw accelerometer в `g`;
- перевести raw gyroscope в `dps`;
- перевести raw temperature в Celsius;
- напечатать красивую строку и JSON-подобную телеметрию.

Главное состояние:

- `s_mpu.addr`
- `s_mpu.whoami`
- `s_mpu.accel_lsb_per_g`
- `s_mpu.gyro_lsb_per_dps`
- `s_mpu.ready`

Главные функции:

- [[04-functions/app_mpu_pretty_init]]
- [[04-functions/app_mpu_pretty_log_line]]
- [[04-functions/app_mpu_i16be]]
- [[04-functions/app_mpu_accel_lsb_per_g]]
- [[04-functions/app_mpu_gyro_lsb_per_dps]]

