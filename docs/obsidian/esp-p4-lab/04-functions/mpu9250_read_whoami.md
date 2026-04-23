# mpu9250_read_whoami

Исходник: `components/mpu9250/src/mpu9250.c`.

`mpu9250_read_whoami()` читает регистр `WHO_AM_I`.

Что делает:

- проверяет `out_whoami`;
- пишет `0x00` в `MPU_REG_PWR_MGMT_1`;
- читает один байт из `MPU_REG_WHO_AM_I`;
- возвращает результат `i2c_bus_read()`.

Запись в `PWR_MGMT_1` нужна, чтобы разбудить MPU перед чтением.

