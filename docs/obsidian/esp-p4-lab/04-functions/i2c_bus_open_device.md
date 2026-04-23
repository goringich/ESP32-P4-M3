# i2c_bus_open_device

Исходник: `components/i2c_bus/src/i2c_bus.c`.

`i2c_bus_open_device()` создает device handle для конкретного I2C адреса.

Что настраивает:

- 7-bit address mode;
- `device_address = addr`;
- `scl_speed_hz = CONFIG_I2C_BUS_FREQ_HZ`;
- ACK check включен.

Функция используется внутри `i2c_bus_read()` и `i2c_bus_write()`.

Это static helper, наружу он не экспортируется.

