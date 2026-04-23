# i2c_bus_probe_addr

Исходник: `components/i2c_bus/src/i2c_bus.c`.

`i2c_bus_probe_addr()` проверяет, отвечает ли устройство на конкретном I2C адресе.

Что делает:

- если bus не создан, возвращает `ESP_ERR_INVALID_STATE`;
- вызывает `i2c_master_probe(s_bus, addr, I2C_XFER_TIMEOUT_MS)`.

Используется в `mpu9250_probe_addr()` для проверки адресов `0x68` и `0x69`.

