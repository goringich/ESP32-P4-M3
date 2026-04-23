# app_stepper_cmd_to_str

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_cmd_to_str()` переводит последний command byte в строку.

Особые случаи:

- `0` -> пустая строка;
- `'\r'` -> `\\r`;
- `'\n'` -> `\\n`;
- иначе возвращается однобуквенная строка.

Функция использует static buffer на 2 символа для обычных команд.

