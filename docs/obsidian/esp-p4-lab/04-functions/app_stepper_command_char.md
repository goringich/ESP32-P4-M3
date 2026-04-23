# app_stepper_command_char

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_command_char()` - публичный bridge для сетевого слоя.

Что делает:

```c
app_stepper_handle_command((uint8_t)cmd);
return ESP_OK;
```

Почему функция нужна:

- `app_stepper_handle_command()` остается static и внутренней;
- `app_net.c` не получает доступ ко всем внутренностям stepper;
- сеть и UART используют один и тот же обработчик команд;
- старый UART-код не удаляется.

См. [[02-architecture/UART and network dual control]].

