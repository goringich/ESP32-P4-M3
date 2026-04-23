# app_mpu_whoami_check

Исходник: `components/app/src/app.c`.

`app_mpu_whoami_check()` проверяет, виден ли MPU-сенсор на I2C.

Что делает:

- печатает блок `MPU WHOAMI CHECK`;
- вызывает `mpu9250_probe_and_read_whoami(&addr, &who)`;
- если сенсор найден, логирует адрес, WHO_AM_I и имя модели;
- если сенсор не найден, деинициализирует I2C bus;
- запускает `i2c_bus_diag_sweep_mpu_pairs()` для перебора возможных SDA/SCL пар.

Почему функция деинициализирует I2C перед sweep:

- основной bus уже занял конкретные GPIO;
- диагностический sweep создает временные bus на разных парах GPIO;
- активный bus надо отпустить, чтобы не конфликтовать с диагностикой.

Связи:

- [[04-functions/mpu9250_probe_and_read_whoami]]
- [[04-functions/i2c_bus_deinit]]
- [[04-functions/i2c_bus_diag_sweep_mpu_pairs]]

