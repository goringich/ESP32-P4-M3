# i2c_bus_deinit

Исходник: `components/i2c_bus/src/i2c_bus.c`.

`i2c_bus_deinit()` освобождает I2C master bus.

Что делает:

- если `s_bus == NULL`, просто выходит;
- вызывает `i2c_del_master_bus(s_bus)`;
- если удаление не удалось, пишет warning;
- при успехе ставит `s_bus = NULL`;
- логирует `bus released`.

Используется перед диагностическим sweep, чтобы временные bus на других GPIO не конфликтовали с основным.

