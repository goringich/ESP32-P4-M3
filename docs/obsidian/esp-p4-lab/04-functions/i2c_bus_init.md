# i2c_bus_init

Исходник: `components/i2c_bus/src/i2c_bus.c`.

`i2c_bus_init()` создает I2C master bus.

Что делает:

- если bus уже создан, возвращает `ESP_OK`;
- при включенном selftest вызывает `i2c_bus_selfcheck_gpio()`;
- читает idle levels SDA/SCL через `i2c_bus_read_lines()`;
- логирует уровни;
- если SDA или SCL low в idle, пишет warning;
- заполняет `i2c_master_bus_config_t`;
- вызывает `i2c_new_master_bus(&bus_cfg, &s_bus)`;
- логирует выбранные GPIO и частоту.

Конфиги:

- `CONFIG_I2C_BUS_SDA_GPIO`
- `CONFIG_I2C_BUS_SCL_GPIO`
- `CONFIG_I2C_BUS_FREQ_HZ`

