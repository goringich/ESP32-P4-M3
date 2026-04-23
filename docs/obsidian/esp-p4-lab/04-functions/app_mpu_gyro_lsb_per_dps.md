# app_mpu_gyro_lsb_per_dps

Исходник: `components/app/src/app_mpu_pretty.c`.

`app_mpu_gyro_lsb_per_dps()` переводит `GYRO_CONFIG` в scale factor.

Варианты:

- `0`: `131.0f`, диапазон `+/-250 dps`;
- `1`: `65.5f`, диапазон `+/-500 dps`;
- `2`: `32.8f`, диапазон `+/-1000 dps`;
- `3`: `16.4f`, диапазон `+/-2000 dps`.

Значение нужно, чтобы перевести raw gyro counts в градусы в секунду.

