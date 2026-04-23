# app_mpu_pretty_init

Исходник: `components/app/src/app_mpu_pretty.c`.

`app_mpu_pretty_init()` подготавливает MPU telemetry layer.

Что делает:

- если `s_mpu.ready`, возвращает `ESP_OK`;
- ищет MPU и читает WHO_AM_I;
- пишет `0` в `PWR_MGMT_1`, чтобы разбудить датчик;
- читает `GYRO_CONFIG`;
- читает `ACCEL_CONFIG`;
- вычисляет scale для gyro и accel;
- сохраняет `whoami`;
- ставит `s_mpu.ready = true`;
- логирует параметры.

Функция вызывается лениво из `app_mpu_pretty_log_line()`.

