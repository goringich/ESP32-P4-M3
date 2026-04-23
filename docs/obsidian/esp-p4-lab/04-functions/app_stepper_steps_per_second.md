# app_stepper_steps_per_second

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_steps_per_second()` переводит задержку шага в шаги в секунду.

Формула:

```c
1000.0f / (float)delay_ms
```

Если `delay_ms == 0`, возвращает `0.0f`, чтобы не делить на ноль.

Используется в status и telemetry.

