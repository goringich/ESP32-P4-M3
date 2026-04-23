# app_mpu_i16be

Исходник: `components/app/src/app_mpu_pretty.c`.

`app_mpu_i16be()` собирает signed 16-bit число из двух байт big-endian.

Формула:

```c
(int16_t)(((uint16_t)hi << 8) | lo)
```

MPU registers хранят 16-bit значения как старший байт, затем младший байт. Поэтому функция нужна для raw accelerometer/gyro/temperature.

