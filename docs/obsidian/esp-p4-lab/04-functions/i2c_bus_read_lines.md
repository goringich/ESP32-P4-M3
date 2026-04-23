# i2c_bus_read_lines

Исходник: `components/i2c_bus/src/i2c_bus.c`.

`i2c_bus_read_lines()` временно читает уровни SDA/SCL как обычные GPIO inputs.

Что делает:

- ставит SDA GPIO в input;
- ставит SCL GPIO в input;
- читает уровни через `gpio_get_level()`;
- возвращает структуру `i2c_lines_t`.

Используется до создания I2C peripheral, чтобы проверить idle состояние линий.

