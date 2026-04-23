# i2c_bus_selfcheck_gpio

Исходник: `components/i2c_bus/src/i2c_bus.c`.

`i2c_bus_selfcheck_gpio()` компилируется только при включенном `CONFIG_I2C_BUS_SELFTEST`.

Что проверяет:

- idle уровни SDA/SCL;
- возможность утянуть SCL в low;
- возврат SCL обратно в high.

Зачем:

- обнаружить проблемы с проводкой;
- увидеть, что линия зажата в low;
- проверить pull-up поведение до старта I2C peripheral.

