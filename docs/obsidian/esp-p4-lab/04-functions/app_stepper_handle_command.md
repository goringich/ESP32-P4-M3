# app_stepper_handle_command

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_handle_command()` - центральный обработчик команд stepper.

Эта функция используется и UART путем, и сетевым путем через `app_stepper_command_char()`.

Команды:

- `h`: help.
- `p`: status.
- `s`: stop.
- `f`: forward.
- `r`: reverse.
- `w`: sweep.
- `1`: один шаг вперед.
- `2`: один шаг назад.
- `a`, `b`, `c`, `d`: удерживать конкретную фазу.
- `+`, `=`: ускорить, уменьшив delay.
- `-`, `_`: замедлить, увеличив delay.
- `z`: отпустить обмотки.

Защита:

- повтор той же команды в пределах `APP_STEPPER_DUPLICATE_CMD_GUARD_MS` игнорируется;
- это помогает не дергать мотор дважды из-за случайного дребезга/дублирования ввода.

