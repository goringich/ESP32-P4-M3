# Source map

Ниже — карта исходников с пояснением, зачем каждый файл нужен в архитектуре.

## Точка входа и верхний уровень

- `main/main.c`
	- минимальная точка входа проекта;
	- пишет лог `boot`;
	- вызывает `app_init()` ровно один раз;
	- затем бесконечно вызывает `app_tick()` и делает `vTaskDelay(pdMS_TO_TICKS(app_tick_delay_ms()))`.

- `CMakeLists.txt`
	- объявляет проект `p4_lab`;
	- подключает инфраструктуру сборки ESP-IDF.

## Главный прикладной компонент `components/app`

- `components/app/src/app.c`
	- собирает подсистемы в единый жизненный цикл;
	- хранит системный статус `app_system_status_t`;
	- хранит I2C/MPU-сводку `app_i2c_status_t`;
	- инициализирует I2C, диагностику MPU, Wi‑Fi, stepper, network API;
	- периодически запускает телеметрию системы и MPU.

- `components/app/src/app_wifi.c`
	- инициализирует `NVS`, `esp_netif`, event loop и Wi‑Fi stack;
	- поднимает SoftAP;
	- при соответствующем `Kconfig` может включить режим `AP+STA`;
	- отслеживает статусы через event handler;
	- отдает состояние через `app_wifi_get_status()`.

- `components/app/src/app_net.c`
	- поднимает встроенный HTTP server из ESP-IDF;
	- публикует REST API и WebSocket endpoint;
	- собирает JSON из статусов `system`, `mpu`, `i2c`, `stepper`, `wifi`;
	- пересылает команды управления шаговиком в общий обработчик.

- `components/app/src/app_stepper.c`
	- управляет GPIO, подключенными к L293D;
	- хранит внутренний state machine двигателя;
	- поддерживает режимы `stop`, `forward`, `reverse`, `sweep`;
	- читает символы из `UART0`;
	- публикует snapshot состояния для сетевого API.

- `components/app/src/app_mpu_pretty.c`
	- лениво инициализирует MPU через уже готовую I2C-шину;
	- читает сырые данные ускорения, гироскопа и температуры;
	- преобразует их в физические величины;
	- печатает форматированную строку телеметрии;
	- обновляет `app_mpu_status_t` для API.

## Компонент шины I2C

- `components/i2c_bus/src/i2c_bus.c`
	- обертка над `driver/i2c_master.h`;
	- создает master bus;
	- умеет быстро сканировать адреса `0x68` и `0x69`;
	- при необходимости делает полный scan `0x03..0x77`;
	- инкапсулирует операции чтения и записи регистров.

- `components/i2c_bus/src/i2c_bus_diag.c`
	- отдельный диагностический инструмент;
	- перебирает заранее зашитые пары GPIO для SDA/SCL;
	- проверяет, не найден ли MPU на других контактах.

## Компонент MPU

- `components/mpu9250/src/mpu9250.c`
	- не является полным драйвером MPU9250;
	- умеет только базовые операции: найти устройство, прочитать `WHO_AM_I`, вернуть имя модели по коду;
	- используется как нижний слой для `app_mpu_pretty.c`.

## Публичные заголовки

- `components/app/include/app.h`
	- базовый API прикладного слоя;
	- структуры `app_system_status_t` и `app_i2c_status_t`.

- `components/app/include/app_wifi.h`
	- `app_wifi_status_t`;
	- API запуска и чтения состояния Wi‑Fi.

- `components/app/include/app_net.h`
	- минимальный API сетевого слоя: старт и периодический tick.

- `components/app/include/app_stepper.h`
	- `app_stepper_snapshot_t`;
	- API управления одной командой и получения снимка состояния.

- `components/app/include/app_mpu_pretty.h`
	- `app_mpu_status_t`;
	- API для инициализации и периодического логирования MPU.

- `components/i2c_bus/include/i2c_bus.h`
	- публичный низкоуровневый интерфейс I2C для других компонентов.

- `components/i2c_bus/include/i2c_bus_diag.h`
	- API диагностики нетипичных пар GPIO для I2C.

- `components/mpu9250/include/mpu9250.h`
	- компактный API probe/WHO_AM_I для сенсора.

## Файлы конфигурации и сборки

- `components/app/Kconfig`
	- переключатели режимов приложения, Wi‑Fi и stepper.

- `components/i2c_bus/Kconfig`
	- выбор GPIO для I2C и частоты шины.

- `sdkconfig`
	- фактические значения конфигурации текущей сборки.

- `sdkconfig.defaults`
	- базовые значения по умолчанию для новых конфигураций.

## Практический вывод

Если нужно понять проект быстро, то читать файлы лучше в таком порядке:

1. `main/main.c`
2. `components/app/src/app.c`
3. `components/app/src/app_stepper.c`
4. `components/app/src/app_net.c`
5. `components/app/src/app_wifi.c`
6. `components/app/src/app_mpu_pretty.c`
7. `components/i2c_bus/src/i2c_bus.c`
8. `components/mpu9250/src/mpu9250.c`

