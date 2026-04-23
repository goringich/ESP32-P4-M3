# i2c_bus_diag_probe_pair

Исходник: `components/i2c_bus/src/i2c_bus_diag.c`.

`i2c_bus_diag_probe_pair()` проверяет одну пару SDA/SCL.

Что делает:

- игнорирует пару, если SDA и SCL одинаковые;
- переводит оба GPIO в input;
- читает idle levels;
- создает временный I2C bus;
- проверяет адреса `0x68` и `0x69`;
- если устройство найдено, пишет warning `FOUND`;
- удаляет временный I2C bus.

Функция static, то есть доступна только внутри `i2c_bus_diag.c`.

