# mpu9250_whoami_name

Исходник: `components/mpu9250/src/mpu9250.c`.

`mpu9250_whoami_name()` переводит значение WHO_AM_I в строку.

Поддерживаемые значения:

- `0x70`: `MPU-6500`;
- `0x71`: `MPU-9250`;
- `0x73`: `MPU-9255/variant`;
- другое: `unknown/clone`.

Это диагностическая функция для логов и telemetry.

