# I2C Kconfig

Файл: `components/i2c_bus/Kconfig`.

Опции:

- `I2C_BUS_SDA_GPIO`: GPIO для SDA.
- `I2C_BUS_SCL_GPIO`: GPIO для SCL.
- `I2C_BUS_FREQ_HZ`: частота I2C.

Текущие значения из `sdkconfig`:

- `CONFIG_I2C_BUS_SDA_GPIO=1`
- `CONFIG_I2C_BUS_SCL_GPIO=2`
- `CONFIG_I2C_BUS_FREQ_HZ=100000`

Частота `100000` Гц - стандартный безопасный режим I2C. Для диагностики проводки и MPU это хороший старт.

