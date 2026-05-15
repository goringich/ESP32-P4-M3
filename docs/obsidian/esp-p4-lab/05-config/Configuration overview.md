# Configuration overview

## Зачем здесь нужен отдельный раздел про конфигурацию

В ESP-IDF проекте значительная часть поведения определяется не только кодом, но и конфигурацией. В `p4_lab` это особенно заметно: через конфиг управляются:

- состав активных подсистем;
- GPIO для I2C и stepper;
- частота I2C;
- параметры Wi‑Fi;
- включение сетевого API;
- параметры UART и LED для stepper.

То есть для полного понимания проекта нужно читать и код, и конфигурацию вместе.

## Главные файлы конфигурации

- `components/app/Kconfig`
- `components/i2c_bus/Kconfig`
- `sdkconfig`
- `sdkconfig.defaults`
- `CMakeLists.txt`

## Роль каждого файла

### `components/app/Kconfig`

Описывает прикладные настройки проекта:

- режим приложения;
- включение tick-логирования;
- Wi‑Fi smoke run;
- параметры SoftAP;
- включение попытки STA-подключения;
- включение HTTP/WebSocket API;
- GPIO и timing для L293D;
- настройки UART stepper;
- optional LED activity.

### `components/i2c_bus/Kconfig`

Описывает инфраструктурные параметры I2C:

- `CONFIG_I2C_BUS_SDA_GPIO`;
- `CONFIG_I2C_BUS_SCL_GPIO`;
- `CONFIG_I2C_BUS_FREQ_HZ`.

### `sdkconfig`

Это итоговая конфигурация текущей сборки. Именно она реально влияет на компиляцию и работу прошивки в данной рабочей копии.

### `sdkconfig.defaults`

Хранит базовые значения по умолчанию, которые особенно важны при создании новой конфигурации или переносе проекта на другое рабочее место.

## Важные настройки `components/app/Kconfig`

### Выбор режима приложения

В `Kconfig` есть выбор:

- `APP_MODE_MPU9250`
- `APP_MODE_L293D_TEST`

Но важно понимать практический нюанс: текущий код уже использует и моторную, и MPU-логику одновременно. Поэтому формально `choice` есть, но архитектурно проект уже вышел за рамки строго одного режима.

### Логирование

- `CONFIG_APP_TICK_LOG`

Когда включено, `app.c` раз в секунду генерирует системную и MPU-телеметрию.

### Wi‑Fi

- `CONFIG_APP_WIFI_SMOKE`
- `CONFIG_APP_WIFI_AP_SSID_PREFIX`
- `CONFIG_APP_WIFI_AP_PASSWORD`
- `CONFIG_APP_WIFI_AP_CHANNEL`
- `CONFIG_APP_WIFI_SCAN_MAX_AP`
- `CONFIG_APP_WIFI_CONNECT`
- `CONFIG_APP_WIFI_SSID`
- `CONFIG_APP_WIFI_PASSWORD`
- `CONFIG_APP_NET_ENABLE`

Из этих параметров складывается сетевое поведение прошивки.

### Stepper / L293D

- `CONFIG_APP_L293D_IN1_GPIO`
- `CONFIG_APP_L293D_IN2_GPIO`
- `CONFIG_APP_L293D_IN3_GPIO`
- `CONFIG_APP_L293D_IN4_GPIO`
- `CONFIG_APP_L293D_STEP_DELAY_MS`
- `CONFIG_APP_STEPPER_UART_BAUD_RATE`
- `CONFIG_APP_STEPPER_LED_ENABLE`
- `CONFIG_APP_STEPPER_LED_GPIO`

Это критическая часть для аппаратной привязки проекта к конкретному стенду.

## Текущие значимые значения конфигурации

По состоянию текущего проекта особенно важны следующие опции:

- `CONFIG_IDF_TARGET="esp32p4"`
- `CONFIG_HTTPD_WS_SUPPORT=y`
- `CONFIG_ESP_WIFI_REMOTE_ENABLED=y`
- `CONFIG_ESP_WIFI_REMOTE_LIBRARY_HOSTED=y`
- `CONFIG_ESP_HOSTED_ENABLED=y`
- `CONFIG_ESP_HOSTED_CP_TARGET_ESP32C6=y`
- `CONFIG_ESP_HOSTED_P4_DEV_BOARD_FUNC_BOARD=y`
- `CONFIG_ESP_HOSTED_SDIO_HOST_INTERFACE=y`
- `CONFIG_APP_MODE_L293D_TEST=y`
- `CONFIG_APP_WIFI_SMOKE=y`
- `CONFIG_APP_NET_ENABLE=y`
- `CONFIG_APP_WIFI_AP_SSID_PREFIX="JC-ESP32P4M3"`
- `CONFIG_APP_WIFI_AP_PASSWORD="esp32p4m3"`
- `CONFIG_APP_WIFI_AP_CHANNEL=1`
- `# CONFIG_APP_WIFI_CONNECT is not set`

## Что это означает в runtime

Из этих значений следует:

- проект собирается под `ESP32-P4`;
- WebSocket support включен;
- сеть построена через hosted Wi‑Fi стек, связанный с `ESP32-C6`;
- активирован режим stepper-стенда;
- при старте поднимается Wi‑Fi smoke/bringup;
- доступен HTTP/WebSocket API;
- устройство поднимает собственную точку доступа;
- попытка подключения к внешнему роутеру сейчас по умолчанию не выполняется.

## Почему `Kconfig` важен для архитектуры

Через конфиг в проекте решаются сразу две задачи:

1. аппаратная параметризация;
2. функциональная композиция прошивки.

Это делает один и тот же код переиспользуемым в разных вариантах стенда без ручного редактирования исходников.

## Что полезно показать в курсовой

В курсовой по этому разделу можно явно подчеркнуть:

- почему в embedded-проекте конфигурация равноправна коду;
- как `Kconfig` помогает переносить проект между стендами;
- как compile-time флаги влияют на состав подсистем;
- как конфиг определяет сетевой и аппаратный профиль устройства.

