# app_mpu_accel_lsb_per_g

Исходник: `components/app/src/app_mpu_pretty.c`.

`app_mpu_accel_lsb_per_g()` переводит `ACCEL_CONFIG` в scale factor.

Варианты:

- `0`: `16384.0f`, диапазон `+/-2g`;
- `1`: `8192.0f`, диапазон `+/-4g`;
- `2`: `4096.0f`, диапазон `+/-8g`;
- `3`: `2048.0f`, диапазон `+/-16g`.

Значение нужно, чтобы перевести raw accelerometer counts в `g`.

