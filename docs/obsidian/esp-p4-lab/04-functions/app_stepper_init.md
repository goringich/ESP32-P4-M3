# app_stepper_init

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_init()` инициализирует подсистему L293D stepper.

Что делает:

- печатает блок `L293D STEPPER UART CONTROL`;
- вызывает `app_stepper_gpio_init()`;
- вызывает `app_stepper_led_init()`;
- вызывает `app_stepper_release()`;
- вызывает `app_stepper_uart_init()`;
- если UART не поднялся, логирует warning, но motor logic оставляет доступной;
- печатает GPIO pins, задержку шага, UART параметры;
- печатает help по командам;
- ставит `sweep_state = APP_STEPPER_SWEEP_FORWARD`;
- переключает режим в `APP_STEPPER_MODE_SWEEP`;
- печатает telemetry `init`.

Важное поведение: ошибка UART не ломает моторную логику. Это нужно, чтобы сетевое управление могло работать даже без UART.

