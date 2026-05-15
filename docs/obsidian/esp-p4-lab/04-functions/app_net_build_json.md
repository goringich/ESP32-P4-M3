# app_net_build_json

Исходник: `components/app/src/app_net.c`.

`app_net_build_json()` собирает общий telemetry JSON.

## Почему эта функция одна из самых важных в проекте

Это центральная функция сетевой сериализации состояния. Через нее почти весь внутренний runtime проекта превращается в единый JSON-документ для HTTP и WebSocket.

Источник данных:

- `app_stepper_get_snapshot(&stepper)`;
- `app_wifi_get_status(&wifi)`.

Но это только часть картины. В текущем коде функция также читает:

- `app_get_system_status(&system)`;
- `app_mpu_get_status(&mpu)`;
- `app_get_i2c_status(&i2c)`.

JSON содержит:

- `ok`;
- `telemetry.system.*`;
- `telemetry.mpu.*`;
- `telemetry.i2c.*`;
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

## Как функция обрабатывает строки и optional-поля

Внутри используется helper `app_net_json_str()`, который:

- возвращает `null`, если строка пустая или отсутствует;
- иначе оборачивает строку в JSON-кавычки.

Это важно для полей вроде:

- ошибок;
- адреса MPU;
- `whoAmI`;
- `model`;
- scan summary.

## Как собирается сводный статус

Функция делает несколько полезных преобразований:

- собирает список I2C-устройств в JSON-массив;
- выбирает IP Wi‑Fi с приоритетом `sta_ip`, затем `ap_ip`;
- нормализует Wi‑Fi error как `null`, если ошибки нет;
- сериализует и stepper, и sensor, и system-данные в один документ.

## Где используется

Эта функция фактически лежит под двумя внешними сценариями:

- `GET /api/telemetry`;
- WebSocket push/response.

То есть один и тот же JSON-слепок используется и для pull-модели, и для push-модели. Это удачное решение: клиент видит одинаковую схему данных независимо от транспорта.

## Ограничения реализации

- JSON строится вручную через `snprintf`;
- структура фиксирована и довольно большая;
- при сильном росте протокола такой стиль станет сложнее сопровождать.

Но для текущего стенда это одна из самых наглядных функций проекта: именно здесь видно, как отдельные подсистемы превращаются в единый внешний API.

Функция возвращает количество записанных байт с учетом защиты от переполнения буфера.

