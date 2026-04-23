# mpu9250_probe_and_read_whoami

Исходник: `components/mpu9250/src/mpu9250.c`.

`mpu9250_probe_and_read_whoami()` объединяет поиск адреса и чтение WHO_AM_I.

Алгоритм:

- проверяет выходные указатели;
- вызывает `mpu9250_probe_addr(out_addr)`;
- если адрес не найден, возвращает ошибку;
- вызывает `mpu9250_read_whoami(*out_addr, out_whoami)`.

Используется в:

- `app_mpu_whoami_check()`;
- `app_mpu_pretty_init()`.

