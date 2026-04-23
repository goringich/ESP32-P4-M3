# app_stepper_emit_telemetry

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_emit_telemetry()` печатает telemetry строку для stepper.

Формат начинается с:

```text
@telemetry
```

Поля:

- kind;
- reason;
- mode;
- sweep_state;
- step_delay_ms;
- steps_per_second;
- phase_index;
- total_steps;
- coils_enabled;
- sweep_steps;
- uart_ready;
- last_command;
- pins;
- led_gpio.

Это текстовая телеметрия для логов/UART. Для HTTP/WebSocket JSON используется отдельная функция `app_net_build_json()`.

