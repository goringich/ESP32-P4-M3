# i2c_bus_diag

Файл: `components/i2c_bus/src/i2c_bus_diag.c`.

Назначение:

- помочь найти правильные пары SDA/SCL, если MPU не найден;
- попробовать набор типичных GPIO пар;
- для каждой пары создать временный I2C bus;
- проверить адреса `0x68` и `0x69`;
- удалить временный bus.

Это диагностический код. Он вызывается из `app_mpu_whoami_check()`, если обычный поиск MPU не сработал.

Главные функции:

- [[04-functions/i2c_bus_diag_sweep_mpu_pairs]]
- [[04-functions/i2c_bus_diag_probe_pair]]

