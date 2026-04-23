# app_net_build_json

Исходник: `components/app/src/app_net.c`.

`app_net_build_json()` собирает общий telemetry JSON.

Источник данных:

- `app_stepper_get_snapshot(&stepper)`;
- `app_wifi_get_status(&wifi)`.

JSON содержит:

- `ok`;
- `telemetry.stepper.mode`;
- `telemetry.stepper.sweepState`;
- `telemetry.stepper.delayMs`;
- `telemetry.stepper.stepsPerSecond`;
- `telemetry.stepper.phaseIndex`;
- `telemetry.stepper.totalSteps`;
- `telemetry.stepper.coilsEnabled`;
- `telemetry.stepper.sweepSteps`;
- `telemetry.stepper.uartReady`;
- `telemetry.stepper.lastCommand`;
- `telemetry.stepper.pins`;
- `telemetry.stepper.ledGpio`;
- `telemetry.wifi.initialized`;
- `telemetry.wifi.apStarted`;
- `telemetry.wifi.staAttempted`;
- `telemetry.wifi.staConnected`;
- `telemetry.wifi.apSsid`;
- `telemetry.wifi.apIp`;
- `telemetry.wifi.staIp`;
- `telemetry.wifi.lastError`.

Функция возвращает количество записанных байт с учетом защиты от переполнения буфера.

