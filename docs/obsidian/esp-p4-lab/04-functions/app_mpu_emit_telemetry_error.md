# app_mpu_emit_telemetry_error

Исходник: `components/app/src/app_mpu_pretty.c`.

`app_mpu_emit_telemetry_error()` печатает telemetry строку ошибки MPU.

Формат:

```text
@telemetry {"kind":"mpu","ready":false,"error":"..."}
```

Ошибка переводится в строку через `esp_err_to_name(err)`.

