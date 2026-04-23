# i2c_bus

Файл: `components/i2c_bus/src/i2c_bus.c`.

Назначение:

- создать I2C master bus;
- проверить idle levels SDA/SCL;
- сканировать устройства;
- читать регистры;
- писать регистры;
- открывать временный device handle на конкретный адрес.

Важная особенность:

`i2c_bus_read()` и `i2c_bus_write()` каждый раз создают device handle через `i2c_bus_open_device()` и потом удаляют его через `i2c_master_bus_rm_device()`. Это проще для маленького проекта, но не самый быстрый вариант для высокочастотных чтений.

Главные функции:

- [[04-functions/i2c_bus_init]]
- [[04-functions/i2c_bus_deinit]]
- [[04-functions/i2c_bus_scan]]
- [[04-functions/i2c_bus_probe_addr]]
- [[04-functions/i2c_bus_read]]
- [[04-functions/i2c_bus_write]]

