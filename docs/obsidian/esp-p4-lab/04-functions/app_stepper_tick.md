# app_stepper_tick

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_tick()` выполняет периодическую работу stepper.

Что делает:

- читает текущее время через `esp_log_timestamp()`;
- если UART готов, вызывает `app_stepper_handle_uart()`;
- раз в секунду печатает heartbeat telemetry;
- если режим `stop`, выходит;
- если режим `sweep`, управляет автоматическим движением вперед/назад и паузами;
- если режим `forward`, делает шаг вперед с учетом задержки;
- если режим `reverse`, делает шаг назад с учетом задержки.

Timing logic:

- каждый шаг разрешен только если прошло `s_stepper.step_delay_ms`;
- для sweep после `APP_STEPPER_SWEEP_STEPS` шагов включается пауза;
- пауза длится `APP_STEPPER_EDGE_PAUSE_MS`.

Связи:

- [[04-functions/app_stepper_handle_uart]]
- [[04-functions/app_stepper_step_forward_once]]
- [[04-functions/app_stepper_step_reverse_once]]
- [[04-functions/app_stepper_release]]

