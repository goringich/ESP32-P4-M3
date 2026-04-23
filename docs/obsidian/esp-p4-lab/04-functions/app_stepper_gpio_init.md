# app_stepper_gpio_init

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_gpio_init()` настраивает четыре GPIO, подключенные к входам L293D.

Пины берутся из Kconfig:

- `CONFIG_APP_L293D_IN1_GPIO`
- `CONFIG_APP_L293D_IN2_GPIO`
- `CONFIG_APP_L293D_IN3_GPIO`
- `CONFIG_APP_L293D_IN4_GPIO`

Настройка:

- mode: `GPIO_MODE_OUTPUT`;
- pull-up: disabled;
- pull-down: disabled;
- interrupt: disabled.

Функция возвращает результат `gpio_config(&cfg)`.

