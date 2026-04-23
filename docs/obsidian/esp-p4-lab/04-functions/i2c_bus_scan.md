# i2c_bus_scan

Исходник: `components/i2c_bus/src/i2c_bus.c`.

`i2c_bus_scan()` сканирует I2C устройства.

Что делает:

- проверяет, что `s_bus` инициализирован;
- снижает шум логов `i2c.master`;
- быстро проверяет адреса MPU `0x68` и `0x69`;
- при включенном `CONFIG_I2C_BUS_SCAN_FULL` сканирует `0x03..0x77`;
- считает found/timeouts/other_err;
- при включенном `CONFIG_I2C_BUS_SCAN_TABLE` печатает таблицу адресов;
- если ничего не найдено, пишет подсказки про GND/VCC, SDA/SCL, pullups и pins.

Важно: функция не переводит SDA/SCL в plain GPIO во время scan, потому что это могло бы отсоединить активную I2C периферию.

