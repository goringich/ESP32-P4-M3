# i2c_bus_log_lines

Исходник: `components/i2c_bus/src/i2c_bus.c`.

`i2c_bus_log_lines()` печатает уровни SDA/SCL.

Аргументы:

- `where`: подпись места вызова;
- `l`: структура с уровнями `sda` и `scl`.

Используется в `i2c_bus_init()` для ранней диагностики проводки.

