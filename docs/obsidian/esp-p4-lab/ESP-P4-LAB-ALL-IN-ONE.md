# ESP P4 Lab — единый экспорт документации

Этот файл автоматически собран из всех markdown-файлов каталога `docs/obsidian/esp-p4-lab`.
Ниже для каждого исходного файла сначала указан его путь, затем идёт точная копия его содержимого.

Всего файлов: 125



---

## [001] 00-index/Config index.md

# Config index

Этот индекс помогает понять, где именно в проекте задается поведение прошивки на уровне конфигурации.

## Общая конфигурация

- [[05-config/Configuration overview]]
- [[05-config/App Kconfig]]
- [[05-config/I2C Kconfig]]
- [[05-config/sdkconfig]]
- [[05-config/sdkconfig.defaults]]
- [[05-config/CMake overview]]
- [[05-config/Header files]]
- [[05-config/Current network configuration]]

Через эти страницы лучше смотреть:

- какие compile-time флаги влияют на сборку;
- какие GPIO и режимы задаются конфигом;
- как `Kconfig`, `sdkconfig` и `sdkconfig.defaults` связаны между собой.

## Эксплуатационные заметки

- [[06-operations/Build and verification]]
- [[06-operations/Runtime WiFi verification without UART]]
- [[06-operations/How to enable STA WiFi]]
- [[06-operations/API examples]]

## Что читать по темам

### Если интересует сеть

- [[05-config/Current network configuration]]
- [[05-config/Configuration overview]]
- [[06-operations/How to enable STA WiFi]]

### Если интересует аппаратная привязка

- [[05-config/I2C Kconfig]]
- [[05-config/App Kconfig]]
- [[05-config/Header files]]

### Если интересует сборка

- [[05-config/CMake overview]]
- [[05-config/sdkconfig]]
- [[05-config/sdkconfig.defaults]]
- [[06-operations/Build and verification]]



---

## [002] 00-index/Function index.md

# Function index

Это навигационный индекс по функциям проекта. Он полезен, когда архитектура уже понятна и нужно быстро перейти к конкретному поведению в коде.

## Entry points

- [[04-functions/app_main]]
- [[04-functions/app_init]]
- [[04-functions/app_tick]]
- [[04-functions/app_tick_delay_ms]]

Эти функции задают жизненный цикл всей прошивки.

## App helpers

- [[04-functions/app_log_color_block]]
- [[04-functions/app_mpu_whoami_check]]
- [[04-functions/app_emit_system_telemetry]]

Это внутренние вспомогательные функции orchestration-слоя `app.c`.

## Wi-Fi

- [[04-functions/app_wifi_smoke_run]]
- [[04-functions/app_wifi_get_status]]
- [[04-functions/app_wifi_event_handler_common]]
- [[04-functions/app_wifi_event_handler]]
- [[04-functions/app_wifi_log_scan_results]]
- [[04-functions/app_wifi_build_ap_ssid]]
- [[04-functions/app_wifi_nvs_init_once]]
- [[04-functions/app_wifi_refresh_status_locked]]
- [[04-functions/app_wifi_auth_to_str]]
- [[04-functions/app_wifi_log_block]]

Используй этот блок, если нужно понять bringup сети, AP/STA-режим, статус Wi‑Fi и событийную модель.

## HTTP/WebSocket

- [[04-functions/app_net_start]]
- [[04-functions/app_net_tick]]
- [[04-functions/app_net_build_json]]
- [[04-functions/app_net_extract_command]]
- [[04-functions/app_net_command_handler]]
- [[04-functions/app_net_ws_handler]]
- [[04-functions/app_net_queue_ws_send]]
- [[04-functions/app_net_ws_send_work]]
- [[04-functions/app_net_telemetry_handler]]
- [[04-functions/app_net_wifi_handler]]
- [[04-functions/app_net_options_handler]]
- [[04-functions/app_net_set_cors]]

Это ключевой набор функций для удаленного API, JSON и WebSocket push.

## Stepper

- [[04-functions/app_stepper_init]]
- [[04-functions/app_stepper_tick]]
- [[04-functions/app_stepper_handle_command]]
- [[04-functions/app_stepper_command_char]]
- [[04-functions/app_stepper_get_snapshot]]
- [[04-functions/app_stepper_gpio_init]]
- [[04-functions/app_stepper_uart_init]]
- [[04-functions/app_stepper_handle_uart]]
- [[04-functions/app_stepper_apply_phase]]
- [[04-functions/app_stepper_release]]
- [[04-functions/app_stepper_step_forward_once]]
- [[04-functions/app_stepper_step_reverse_once]]
- [[04-functions/app_stepper_set_mode]]
- [[04-functions/app_stepper_apply_named_phase]]
- [[04-functions/app_stepper_delay_adjust_delta_ms]]
- [[04-functions/app_stepper_emit_telemetry]]
- [[04-functions/app_stepper_log_block]]
- [[04-functions/app_stepper_mode_to_str]]
- [[04-functions/app_stepper_steps_per_second]]
- [[04-functions/app_stepper_sweep_state_to_str]]
- [[04-functions/app_stepper_cmd_to_str]]
- [[04-functions/app_stepper_log_timing]]
- [[04-functions/app_stepper_print_help]]
- [[04-functions/app_stepper_print_status]]
- [[04-functions/app_stepper_led_init]]
- [[04-functions/app_stepper_led_set]]
- [[04-functions/app_stepper_led_toggle]]

Этот блок покрывает двигатель, UART-управление, автоматический sweep и snapshot API для сети.

## MPU

- [[04-functions/app_mpu_pretty_init]]
- [[04-functions/app_mpu_pretty_log_line]]
- [[04-functions/app_mpu_i16be]]
- [[04-functions/app_mpu_accel_lsb_per_g]]
- [[04-functions/app_mpu_gyro_lsb_per_dps]]
- [[04-functions/app_mpu_emit_telemetry_ready]]
- [[04-functions/app_mpu_emit_telemetry_error]]
- [[04-functions/mpu9250_probe_addr]]
- [[04-functions/mpu9250_read_whoami]]
- [[04-functions/mpu9250_probe_and_read_whoami]]
- [[04-functions/mpu9250_whoami_name]]

Здесь собраны функции инициализации MPU, пересчета сырых данных и базового sensor-discovery слоя.

## I2C

- [[04-functions/i2c_bus_init]]
- [[04-functions/i2c_bus_deinit]]
- [[04-functions/i2c_bus_scan]]
- [[04-functions/i2c_bus_probe_addr]]
- [[04-functions/i2c_bus_read]]
- [[04-functions/i2c_bus_write]]
- [[04-functions/i2c_bus_open_device]]
- [[04-functions/i2c_bus_read_lines]]
- [[04-functions/i2c_bus_log_lines]]
- [[04-functions/i2c_bus_log_scan_table]]
- [[04-functions/i2c_bus_selfcheck_gpio]]
- [[04-functions/i2c_bus_diag_sweep_mpu_pairs]]
- [[04-functions/i2c_bus_diag_probe_pair]]

Это базовый low-level индекс по I2C и диагностике шины.

## Самые важные страницы, если времени мало

Если нужен короткий список самых полезных function docs, начни с них:

- [[04-functions/app_main]]
- [[04-functions/app_init]]
- [[04-functions/app_tick]]
- [[04-functions/app_wifi_smoke_run]]
- [[04-functions/app_net_build_json]]
- [[04-functions/app_stepper_tick]]
- [[04-functions/i2c_bus_init]]
- [[04-functions/mpu9250_probe_and_read_whoami]]
- [[04-functions/app_mpu_pretty_init]]

Этот набор почти полностью раскрывает жизненный цикл, сеть, stepper, I2C и MPU.



---

## [003] 00-index/README.md

# ESP P4 Lab Documentation

Это корневая страница внутренней технической документации по проекту `p4_lab`.

Документация нужна не только чтобы "понять, где что лежит", а чтобы по ней можно было:

- быстро восстановить архитектуру проекта без чтения всего кода подряд;
- объяснить, как устроена прошивка, на защите или в курсовой;
- понять, какие подсистемы уже реализованы, а какие являются заготовками;
- брать готовые формулировки, схемы, цепочки вызовов и примеры кода.

## Что делает проект

Проект представляет собой прошивку для `ESP32-P4`, в которой объединены несколько учебно-практических задач:

- инициализация и диагностика `I2C`;
- обнаружение и опрос датчика семейства `MPU-9250`;
- управление шаговым двигателем через драйвер `L293D`;
- локальное управление через `UART`;
- сетевой доступ к состоянию и управлению через `Wi-Fi + HTTP + WebSocket`;
- периодическая выдача телеметрии в лог и в JSON.

По сути это лабораторный стенд, где одна прошивка показывает сразу несколько типовых подсистем встраиваемого ПО:

- low-level работа с шинами и GPIO;
- прикладной orchestration слой;
- сеть и API;
- телеметрия и диагностика;
- конфигурирование через `Kconfig`/`sdkconfig`.

## Краткая архитектура

Система разбита на понятные блоки:

- `main/main.c` — минимальная точка входа ESP-IDF;
- `components/app/src/app.c` — общий координатор жизненного цикла;
- `components/app/src/app_wifi.c` — запуск Wi‑Fi и хранение статуса;
- `components/app/src/app_net.c` — HTTP/WebSocket сервер и JSON API;
- `components/app/src/app_stepper.c` — логика шагового двигателя и команд;
- `components/app/src/app_mpu_pretty.c` — опрос MPU и форматирование телеметрии;
- `components/i2c_bus/src/i2c_bus.c` — универсальные операции I2C;
- `components/i2c_bus/src/i2c_bus_diag.c` — диагностика пар SDA/SCL;
- `components/mpu9250/src/mpu9250.c` — минимальный слой probe/WHO_AM_I.

Ключевая инженерная идея проекта: все внешние интерфейсы сводятся к небольшому набору публичных API, а `main` остается почти пустым.

## Что важно знать до чтения

1. Это не полный промышленный продукт, а учебно-исследовательская прошивка.
2. Некоторые функции есть как задел на будущее, но не везде уже встроены в активный runtime.
3. Документация ниже старается описывать именно **фактическое поведение текущего кода**, а не желаемое состояние.
4. Сеть сейчас строится вокруг SoftAP, а логика двигателя доступна и по UART, и через HTTP/WebSocket.

## Рекомендуемый маршрут чтения

Если нужно быстро войти в проект:

- [[00-index/Reading order]]
- [[02-architecture/System overview]]
- [[02-architecture/Boot and main loop]]
- [[02-architecture/Runtime data flow]]
- [[03-components/app component]]
- [[03-components/app_stepper]]
- [[03-components/app_net]]
- [[03-components/app_wifi]]
- [[03-components/i2c_bus]]
- [[03-components/mpu9250]]
- [[05-config/Configuration overview]]
- [[06-operations/Build and verification]]

Если нужен справочник:

- [[00-index/Function index]]
- [[00-index/Config index]]
- [[00-index/Source map]]

Если нужен материал именно под связный текст курсовой:

- [[08-course-paper/README]]
- [[08-course-paper/Technologies and stack]]
- [[08-course-paper/Engineering decisions]]
- [[08-course-paper/Current limitations]]
- [[08-course-paper/Future development]]

## Главные исходники

- `main/main.c`
- `components/app/src/app.c`
- `components/app/src/app_wifi.c`
- `components/app/src/app_net.c`
- `components/app/src/app_stepper.c`
- `components/app/src/app_mpu_pretty.c`
- `components/i2c_bus/src/i2c_bus.c`
- `components/i2c_bus/src/i2c_bus_diag.c`
- `components/mpu9250/src/mpu9250.c`
- `components/app/Kconfig`
- `components/i2c_bus/Kconfig`
- `sdkconfig`
- `sdkconfig.defaults`

## Что уже можно использовать в курсовой

Из этой базы уже можно брать:

- описание слоев архитектуры;
- последовательность загрузки и основного цикла;
- описание шины I2C и минимального драйверного слоя для MPU;
- описание сетевого API;
- описание схемы двойного управления двигателем;
- примеры структур состояния и JSON телеметрии;
- объяснение, как `Kconfig` влияет на состав функциональности.

Для более связного академического текста теперь также есть отдельный слой:

- стек технологий и платформы;
- инженерные решения по архитектуре;
- ограничения текущего прототипа;
- направления дальнейшего развития.

## Что сознательно не покрывается здесь

- `stepper-remote/backend`;
- `stepper-remote/frontend`;
- исходники внешнего SDK `esp-idf`;
- временные файлы сборки в `build/`.

Для них имеет смысл делать отдельный граф документации, чтобы не смешивать прикладную логику проекта с инфраструктурой SDK.


---

## [004] 00-index/Reading order.md

# Reading order

Этот файл задает не просто список страниц, а несколько разных маршрутов чтения в зависимости от цели.

## Базовый маршрут: быстро понять весь проект

Если нужно получить цельную картину прошивки, лучше идти в таком порядке:

1. [[00-index/README]]
2. [[01-concepts/ESP-IDF basics]]
3. [[01-concepts/FreeRTOS loop model]]
4. [[01-concepts/ESP error handling]]
5. [[01-concepts/WiFi AP STA basics]]
6. [[01-concepts/HTTP and WebSocket basics]]
7. [[01-concepts/I2C basics]]
8. [[01-concepts/Stepper and L293D basics]]
9. [[02-architecture/System overview]]
10. [[02-architecture/Boot and main loop]]
11. [[02-architecture/Runtime data flow]]
12. [[02-architecture/WiFi HTTP WebSocket architecture]]
13. [[02-architecture/UART and network dual control]]
14. [[02-architecture/Telemetry architecture]]
15. [[03-components/app component]]
16. [[03-components/app_wifi]]
17. [[03-components/app_net]]
18. [[03-components/app_stepper]]
19. [[03-components/i2c_bus]]
20. [[03-components/mpu9250]]
21. [[05-config/Configuration overview]]
22. [[06-operations/Build and verification]]

Этот маршрут лучше всего подходит, если нужно потом писать связный обзор проекта для курсовой.

## Маршрут: только сеть и удаленное управление

Если задача — понять Wi‑Fi, HTTP, WebSocket и API, читай:

- [[02-architecture/WiFi HTTP WebSocket architecture]]
- [[02-architecture/UART and network dual control]]
- [[03-components/app_wifi]]
- [[03-components/app_net]]
- [[04-functions/app_wifi_smoke_run]]
- [[04-functions/app_net_start]]
- [[04-functions/app_net_build_json]]
- [[04-functions/app_net_tick]]
- [[06-operations/API examples]]
- [[06-operations/Runtime WiFi verification without UART]]

## Маршрут: только мотор и локальное управление

Если нужно быстро понять stepper и старое UART-управление:

- [[02-architecture/UART and network dual control]]
- [[03-components/app_stepper]]
- [[04-functions/app_stepper_init]]
- [[04-functions/app_stepper_tick]]
- [[04-functions/app_stepper_handle_command]]
- [[04-functions/app_stepper_get_snapshot]]

## Маршрут: только сенсорная часть и I2C

Если нужен MPU/I2C-путь:

- [[01-concepts/I2C basics]]
- [[03-components/i2c_bus]]
- [[03-components/mpu9250]]
- [[04-functions/i2c_bus_init]]
- [[04-functions/i2c_bus_scan]]
- [[04-functions/mpu9250_probe_and_read_whoami]]
- [[04-functions/app_mpu_pretty_init]]
- [[04-functions/app_mpu_pretty_log_line]]

## Когда использовать индексы

После обзорного чтения лучше переходить к индексам:

- [[00-index/Function index]] — если нужна навигация по поведению кода;
- [[00-index/Config index]] — если нужно понять, что задается конфигом;
- [[00-index/Source map]] — если нужно быстро найти физические файлы.

## Практический совет

Для подготовки курсовой лучше читать именно слоями:

1. концепции;
2. архитектура;
3. компоненты;
4. функции;
5. конфигурация;
6. эксплуатация и верификация.

Так текст потом сам собирается в правильную структуру главы. Почти как будто проект сам пишет пояснительную записку, если его достаточно долго читать. Почти.


---

## [005] 00-index/Source map.md

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



---

## [006] 01-concepts/ESP error handling.md

# ESP error handling

ESP-IDF функции обычно возвращают `esp_err_t`.

В проекте используются основные значения:

- `ESP_OK`: операция успешна.
- `ESP_FAIL`: общая ошибка.
- `ESP_ERR_INVALID_ARG`: неверный аргумент функции.
- `ESP_ERR_INVALID_STATE`: подсистема не инициализирована или уже в другом состоянии.
- `ESP_ERR_NOT_FOUND`: устройство не найдено.
- `ESP_ERR_NOT_SUPPORTED`: возможность не включена в конфиге.
- `ESP_ERR_NO_MEM`: не хватило памяти.
- `ESP_ERR_INVALID_SIZE`: слишком большой буфер или размер.
- `ESP_ERR_TIMEOUT`: таймаут операции.

Для печати человекочитаемого имени ошибки используется:

```c
esp_err_to_name(err)
```

В коде встречаются два стиля:

- вернуть ошибку вызывающему коду;
- использовать `ESP_ERROR_CHECK(...)`, если ошибка считается фатальной на этапе инициализации.

См. [[04-functions/app_wifi_smoke_run]], [[04-functions/i2c_bus_read]], [[04-functions/app_net_start]].



---

## [007] 01-concepts/ESP-IDF basics.md

# ESP-IDF basics

ESP-IDF - это официальный фреймворк Espressif для прошивок ESP32-семейства.

В этом проекте он дает:

- точку входа `app_main()`;
- компоненты через `idf_component_register`;
- конфигурацию через `Kconfig`, `menuconfig`, `sdkconfig`;
- драйверы GPIO, UART, I2C, Wi-Fi;
- HTTP server;
- FreeRTOS scheduler;
- систему логирования `ESP_LOGI`, `ESP_LOGW`, `ESP_LOGE`;
- тип ошибок `esp_err_t`.

Проект не является обычной Linux-программой. После прошивки код работает на микроконтроллере. Поэтому `main/main.c` не завершает программу, а входит в бесконечный цикл:

```c
while (1) {
  app_tick();
  vTaskDelay(pdMS_TO_TICKS(app_tick_delay_ms()));
}
```

См. [[02-architecture/Boot and main loop]].



---

## [008] 01-concepts/FreeRTOS loop model.md

# FreeRTOS loop model

ESP-IDF запускает приложение внутри FreeRTOS. В проекте нет отдельной задачи для каждой подсистемы приложения. Вместо этого используется простой кооперативный цикл:

- `app_main()` вызывает `app_init()`;
- дальше в бесконечном цикле вызывает `app_tick()`;
- между итерациями делает `vTaskDelay(...)`.

Это означает:

- функции `*_tick()` не должны надолго блокировать;
- периодический код проверяет время через `esp_log_timestamp()`;
- HTTP server и Wi-Fi имеют свои внутренние задачи внутри ESP-IDF;
- наше приложение периодически кормит их данными, например через `app_net_tick()`.

Главная задержка цикла задается в `components/app/src/app.c`:

```c
#define APP_MAIN_TICK_MS 5U
```

См. [[04-functions/app_tick]] и [[04-functions/app_tick_delay_ms]].



---

## [009] 01-concepts/HTTP and WebSocket basics.md

# HTTP and WebSocket basics

Проект использует две сетевые модели:

- HTTP request/response для точечных запросов;
- WebSocket для постоянного соединения и периодической телеметрии.

HTTP endpoints:

- `GET /api/telemetry`: возвращает общий JSON с состоянием stepper и Wi-Fi.
- `GET /api/wifi`: возвращает только Wi-Fi status.
- `POST /api/command`: принимает команду для stepper.
- `OPTIONS /*`: отвечает на CORS preflight.

WebSocket endpoint:

- `GET /ws`: WebSocket handshake;
- входящее текстовое сообщение может содержать команду;
- раз в секунду `app_net_tick()` рассылает telemetry JSON всем WebSocket-клиентам.

См. [[03-components/app_net]], [[04-functions/app_net_ws_handler]], [[04-functions/app_net_tick]].



---

## [010] 01-concepts/I2C basics.md

# I2C basics

I2C - это двухпроводная шина:

- `SDA`: линия данных;
- `SCL`: линия тактового сигнала.

В проекте I2C используется для MPU9250 или совместимого IMU-сенсора.

Важные детали:

- адрес MPU обычно `0x68` или `0x69`;
- перед чтением регистра master отправляет адрес регистра;
- затем читает нужное количество байт;
- линии должны быть подтянуты вверх;
- если `SDA` или `SCL` в idle состоянии равны `0`, это часто признак проблемы проводки, питания или подтяжек.

Код I2C вынесен в `components/i2c_bus`.

См. [[03-components/i2c_bus]], [[04-functions/i2c_bus_init]], [[04-functions/i2c_bus_scan]].



---

## [011] 01-concepts/Stepper and L293D basics.md

# Stepper and L293D basics

Шаговый двигатель управляется последовательностью фаз. В проекте фаза описывает четыре входа L293D:

- `IN1`
- `IN2`
- `IN3`
- `IN4`

L293D - это драйвер мотора. Микроконтроллер не должен напрямую питать обмотки двигателя, он только выставляет логические уровни на входах драйвера.

Последовательность фаз в проекте:

```c
{1, 0, 1, 0, "phase A"}
{0, 1, 1, 0, "phase B"}
{0, 1, 0, 1, "phase C"}
{1, 0, 0, 1, "phase D"}
```

Движение вперед - проход по фазам вперед. Движение назад - проход по фазам в обратную сторону.

См. [[03-components/app_stepper]], [[04-functions/app_stepper_step_forward_once]], [[04-functions/app_stepper_step_reverse_once]].



---

## [012] 01-concepts/WiFi AP STA basics.md

# WiFi AP STA basics

## Два режима, которые использует проект

В проекте предусмотрены два практически важных режима работы Wi‑Fi:

- `AP` — ESP создает собственную точку доступа;
- `APSTA` — ESP одновременно поднимает свою точку доступа и подключается к внешнему роутеру как клиент.

Важно: в **текущей конфигурации проекта по умолчанию используется именно `WIFI_MODE_AP`**, потому что `CONFIG_APP_WIFI_CONNECT` выключен. Режим `APSTA` включается только при специальной настройке STA-подключения.

## Что означает `AP`

В режиме `AP`:

- ESP создает собственную Wi‑Fi сеть;
- компьютер или телефон может подключиться напрямую к устройству;
- сетевой API доступен без внешнего роутера.

Для лабораторного стенда это особенно удобно: система автономна и не зависит от инфраструктуры помещения.

## Что означает `APSTA`

В режиме `APSTA`:

- ESP все еще держит собственную точку доступа;
- одновременно она подключается к существующей Wi‑Fi сети как клиент;
- появляется возможность обращаться к устройству и через SoftAP, и через внешний роутер.

Это полезно, если устройство нужно встроить в более общую сеть, но не потерять прямой fallback-доступ.

## Зачем в проекте нужны оба варианта

- без роутера можно подключиться напрямую к ESP через ее AP;
- при наличии роутера ESP может быть участником общей сети;
- HTTP и WebSocket API доступны поверх Wi‑Fi;
- UART остается резервным локальным каналом диагностики и управления.

## Какие настройки управляют AP

Точка доступа настраивается через:

- `CONFIG_APP_WIFI_AP_SSID_PREFIX`
- `CONFIG_APP_WIFI_AP_PASSWORD`
- `CONFIG_APP_WIFI_AP_CHANNEL`

## Какие настройки включают STA

STA-подключение включается отдельно через:

- `CONFIG_APP_WIFI_CONNECT`
- `CONFIG_APP_WIFI_SSID`
- `CONFIG_APP_WIFI_PASSWORD`

Только после этого `app_wifi.c` начинает выбирать режим `WIFI_MODE_APSTA`.

См. также:

- [[03-components/app_wifi]]
- [[06-operations/How to enable STA WiFi]]



---

## [013] 02-architecture/Boot and main loop.md

# Boot and main loop

## Общая идея

В проекте используется очень простая и наглядная модель жизненного цикла:

- один вход в систему через `app_main()`;
- один этап инициализации `app_init()`;
- один бесконечный прикладной цикл `app_tick()`.

Для учебного embedded-проекта это удачная архитектура: она легко объясняется, хорошо наблюдается в логах и не требует множества отдельных задач FreeRTOS ради базовой демонстрации работы системы.

## Стартовая цепочка

Фактическая последовательность запуска такая:

1. ESP-IDF вызывает `app_main()` из `main/main.c`.
2. `app_main()` пишет лог `boot`.
3. `app_main()` вызывает `app_init()`.
4. `app_init()` поднимает подсистемы.
5. После возврата из `app_init()` функция `app_main()` входит в бесконечный цикл.
6. На каждой итерации вызывается `app_tick()`.
7. Между итерациями выполняется `vTaskDelay(pdMS_TO_TICKS(app_tick_delay_ms()))`.

В текущем коде `app_tick_delay_ms()` возвращает `5 ms`, то есть базовый цикл выполняется с частотой порядка 200 Гц, если никакая из подсистем не тормозит выполнение сильнее.

## Почему `main` оставлен минимальным

Файл `main/main.c` сознательно почти пустой. Это полезно по нескольким причинам:

- `main` не превращается в свалку инфраструктурного кода;
- перенос логики между проектами упрощается;
- жизненный цикл приложения читается буквально в нескольких строках;
- вся прикладная композиция сосредоточена в `components/app`.

Для курсовой это хороший пример разделения входной точки и прикладного orchestration-слоя.

## Что делает `app_init()`

`app_init()` отвечает за разовый bringup подсистем.

В текущей реализации он делает:

- настраивает уровни логирования;
- выполняет `i2c_bus_init()`;
- запускает `i2c_bus_scan()`;
- выполняет `app_mpu_whoami_check()`;
- при включенном `CONFIG_APP_WIFI_SMOKE` запускает `app_wifi_smoke_run()`;
- при включенном `CONFIG_APP_MODE_L293D_TEST` запускает `app_stepper_init()`;
- при включенном `CONFIG_APP_NET_ENABLE` и готовой сети вызывает `app_net_start()`.

Здесь видно, что `app_init()` не содержит тяжёлой доменной логики каждой подсистемы. Он только управляет порядком запуска.

## Что делает `app_tick()`

`app_tick()` — это периодический диспетчер фоновой активности.

В текущем коде он может вызывать:

- `app_stepper_tick()` — обслуживание state machine двигателя;
- `app_net_tick()` — WebSocket push-рассылку;
- system telemetry и MPU telemetry, если включен `CONFIG_APP_TICK_LOG`.

### Периодическая телеметрия

При включенном `CONFIG_APP_TICK_LOG` функция раз в секунду:

- обновляет system status;
- печатает `@telemetry` для системы;
- вызывает `app_mpu_pretty_log_line()`;
- в случае ошибки MPU записывает `last_error` в системный статус.

Таким образом, быстрый основной цикл работает каждые `5 ms`, а тяжёлая телеметрия ограничена внутренним периодом `APP_MPU_LOG_PERIOD_MS = 1000 ms`.

## Почему выбран tick-loop, а не набор отдельных задач

У такого подхода есть плюсы:

- проще отладка;
- проще объяснение архитектуры;
- меньше многопоточности и гонок;
- компактнее код для лабораторной работы.

Есть и ограничения:

- подсистемы делят один execution path;
- если одна операция станет слишком долгой, пострадает ритм общего цикла;
- при росте проекта может потребоваться отдельная RTOS-задача для сети, сенсора или управления двигателем.

Для текущего стенда этот компромисс выглядит разумным.

## Практический смысл для проекта

Именно через эту схему объясняется всё дальнейшее поведение:

- почему stepper двигается даже без внешних команд;
- почему WebSocket push идет периодически;
- почему MPU лог появляется раз в секунду;
- почему большинство ошибок отражаются в status-структурах, а не только в логах.

См. также:

- [[04-functions/app_main]]
- [[04-functions/app_init]]
- [[04-functions/app_tick]]
- [[02-architecture/Runtime data flow]]



---

## [014] 02-architecture/Component dependency graph.md

# Component dependency graph

Компоненты ESP-IDF:

```text
main
  -> app

app
  -> i2c_bus
  -> mpu9250
  -> esp_driver_gpio
  -> esp_driver_uart
  -> esp_wifi
  -> esp_event
  -> esp_http_server
  -> esp_netif
  -> nvs_flash

mpu9250
  -> i2c_bus

i2c_bus
  -> driver
  -> esp_timer
```

Эта структура задается в:

- `components/app/CMakeLists.txt`
- `components/i2c_bus/CMakeLists.txt`
- `components/mpu9250/CMakeLists.txt`
- `main/CMakeLists.txt`

См. [[05-config/CMake overview]].



---

## [015] 02-architecture/Runtime data flow.md

# Runtime data flow

Этот раздел описывает, как реальные данные и команды проходят через систему во время выполнения.

## 1. Поток запуска системы

После загрузки микроконтроллера выполняется следующий сценарий:

1. `app_main()` пишет лог `boot`.
2. `app_main()` вызывает `app_init()`.
3. `app_init()` по очереди поднимает:
	- I2C;
	- I2C scan;
	- MPU WHO_AM_I check;
	- Wi‑Fi smoke run, если включен;
	- stepper subsystem, если включен режим `L293D_TEST`;
	- HTTP/WebSocket API, если включена сеть и Wi‑Fi успешно поднят.
4. Затем `app_main()` переходит в бесконечный цикл `app_tick()`.

Идея в том, что тяжелая инициализация выполняется один раз, а дальше система живет за счет коротких периодических вызовов.

## 2. Поток управления шаговым двигателем

### Через UART

Путь данных:

`UART0` → `app_stepper_handle_uart()` → `app_stepper_handle_command()` → изменение `s_stepper`

Подробно:

- `app_stepper_tick()` опрашивает UART, если `uart_ready == true`;
- считанные байты перебираются по одному;
- каждый символ интерпретируется как команда (`f`, `r`, `s`, `w`, `+`, `-`, и т.д.);
- обработчик обновляет внутренний state machine двигателя.

### Через HTTP

Путь данных:

HTTP `POST /api/command` → `app_net_command_handler()` → `app_net_extract_command()` → `app_stepper_command_char()` → `app_stepper_handle_command()`

Сетевой слой не знает, как именно устроены фазы двигателя. Он только выделяет символ команды и передает его вниз.

### Через WebSocket

Путь данных:

WebSocket text frame → `app_net_ws_handler()` → `app_net_extract_command()` → `app_stepper_command_char()` → `app_stepper_handle_command()`

Это тот же самый исполнительный путь, что и в HTTP. Разница только в транспорте.

## 3. Поток вычисления шага двигателя

Даже если новых команд нет, `app_stepper_tick()` продолжает обслуживать state machine.

### В режиме `sweep`

Алгоритм такой:

- двигатель идет вперед до `APP_STEPPER_SWEEP_STEPS`;
- затем делается пауза `APP_STEPPER_EDGE_PAUSE_MS`;
- после этого двигатель идет назад;
- потом снова пауза;
- цикл повторяется.

Внутри этого механизма используются:

- `s_stepper.mode`;
- `s_stepper.sweep_state`;
- `s_stepper.last_step_ms`;
- `s_stepper.pause_started_ms`;
- `s_stepper.moved_steps_in_leg`.

Физическое движение реализуется через последовательное включение фаз из массива `s_phases`.

## 4. Поток получения телеметрии MPU

Путь данных:

`app_tick()` → `app_mpu_pretty_log_line()` → `app_mpu_pretty_init()` → `i2c_bus_read()` → вычисление физических значений → лог + status + telemetry line

Что происходит по шагам:

1. Раз в секунду `app.c` решает, что пора вывести телеметрию.
2. Если MPU еще не инициализирован, вызывается `app_mpu_pretty_init()`.
3. Через `mpu9250_probe_and_read_whoami()` определяется адрес и код `WHO_AM_I`.
4. Через `i2c_bus_read()` читаются `GYRO_CONFIG`, `ACCEL_CONFIG`, а затем блок данных с `ACCEL_XOUT_H`.
5. Сырые 16-битные значения переводятся в:
	- ускорения в `g`;
	- угловые скорости в `dps`;
	- температуру в `°C`.
6. Результат одновременно:
	- печатается в красивом текстовом виде;
	- сохраняется в `app_mpu_status_t`;
	- публикуется как строка `@telemetry {...}`.

## 5. Поток системной телеметрии

Раз в секунду `app.c` также обновляет общий статус системы:

- `ready`;
- `uptime_ms`;
- `tick`;
- `tick_delay_ms`;
- `firmware`;
- `app_mode`;
- `last_error`.

Затем печатается отдельная telemetry-строка вида:

```text
@telemetry {"kind":"system", ...}
```

Это важно, потому что системная телеметрия и сенсорная телеметрия формируются независимо, но на одинаковой идее — выдавать машинно-читаемый JSON в лог.

## 6. Поток сборки JSON для сети

Путь данных:

`app_net_build_json()` ← `app_stepper_get_snapshot()`
`app_net_build_json()` ← `app_wifi_get_status()`
`app_net_build_json()` ← `app_get_system_status()`
`app_net_build_json()` ← `app_mpu_get_status()`
`app_net_build_json()` ← `app_get_i2c_status()`

Это один из самых важных архитектурных моментов.

`app_net` ничего не "вытаскивает" из чужих внутренних static-переменных. Он получает готовые слепки состояния через публичный API. В результате:

- связи между компонентами слабее;
- сетевой слой проще менять;
- состояние удобно сериализовать;
- документация на API становится понятнее.

## 7. Поток отдачи данных наружу

### HTTP pull-модель

- `GET /api/telemetry` → возвращает полный JSON состояния;
- `GET /api/wifi` → возвращает Wi‑Fi статус.

### WebSocket push-модель

Раз в секунду `app_net_tick()`:

- получает список клиентских сокетов;
- проверяет, какие из них являются WebSocket-клиентами;
- собирает единый JSON;
- ставит асинхронную отправку через `httpd_queue_work()`.

Эта схема удобна для web-dashboard: клиент не обязан постоянно опрашивать REST endpoint.

## 8. Поток ошибок и деградации

В проекте предусмотрена мягкая деградация, а не только "успех или аварийный стоп".

Примеры:

- если I2C init не удался, `app_init()` пишет ошибку и прекращает дальнейшую инициализацию;
- если MPU не найден, выполняется дополнительная диагностика пар GPIO;
- если Wi‑Fi поднять не удалось, сетевой API не стартует;
- если UART driver не поднялся, логика двигателя все равно остается доступной внутри прошивки и через сетевой слой;
- ошибки MPU записываются в `last_error` и публикуются в телеметрии.

## 9. Главная архитектурная развязка

В текущем проекте особенно важно следующее разделение:

- `app_net` не знает внутренних enum и state machine двигателя;
- `app_net` не трогает GPIO напрямую;
- `app_wifi` не знает про шаговый двигатель;
- `app_stepper` не знает ничего про HTTP server и WebSocket;
- `app_mpu_pretty` не знает ничего про HTTP, но публикует состояние, которое сеть потом читает;
- `app.c` выступает единственным orchestration-слоем.

Именно это делает проект пригодным для масштабирования и хорошим примером для пояснения в курсовой работе.



---

## [016] 02-architecture/System overview.md

# System overview

## Назначение системы

Прошивка `p4_lab` — это учебно-прикладная embedded-система для `ESP32-P4`, в которой одновременно демонстрируются несколько важных подсистем:

- циклическая архитектура приложения поверх `FreeRTOS`;
- конфигурируемая работа с `I2C`;
- обнаружение и опрос `MPU-9250`;
- управление шаговым двигателем через `L293D`;
- локальное управление через `UART`;
- удаленное управление и чтение телеметрии через `Wi‑Fi`, `HTTP` и `WebSocket`.

Проект хорошо подходит как основа для курсовой, потому что в нем есть и работа с железом, и сетевой API, и конфигурируемая архитектура, и телеметрия.

## Слои архитектуры

Прошивка разделена на несколько уровней ответственности.

### 1. Входной слой

- `main/main.c`

Этот слой намеренно минимален. Он не знает деталей ни про Wi‑Fi, ни про I2C, ни про шаговый двигатель. Его задача — запустить прикладной слой и поддерживать бесконечный цикл:

- `app_init()` один раз;
- `app_tick()` в цикле;
- задержка между итерациями через `app_tick_delay_ms()`.

### 2. Прикладной координационный слой

- `components/app/src/app.c`

Здесь собрана общая логика жизненного цикла. Файл:

- инициализирует подсистемы в нужном порядке;
- хранит системный статус;
- хранит сводный статус I2C/MPU обнаружения;
- решает, запускать ли сетевой API;
- раз в секунду порождает телеметрию.

Это фактический центр композиции всего проекта.

### 3. Инфраструктурные и прикладные модули

- `app_wifi` — сеть;
- `app_net` — API и транспорт JSON/WS;
- `app_stepper` — исполнительный механизм;
- `app_mpu_pretty` — сенсорная телеметрия;
- `i2c_bus` — базовая шина;
- `mpu9250` — минимальный sensor helper.

## Схема связей между модулями

В текущей реализации зависимости выглядят так:

- `main` зависит только от `app`;
- `app` зависит от `app_wifi`, `app_net`, `app_stepper`, `app_mpu_pretty`, `i2c_bus`, `mpu9250`;
- `app_net` зависит от публичных snapshot/status API других подсистем;
- `app_mpu_pretty` зависит от `i2c_bus` и `mpu9250`;
- `mpu9250` зависит от `i2c_bus`.

Важно, что сетевой слой **не управляет GPIO напрямую** и **не работает с внутренними enum stepper напрямую**. Он общается с моторной подсистемой через маленький публичный API:

- `app_stepper_command_char()`;
- `app_stepper_get_snapshot()`.

Это хорошее архитектурное решение: транспорт и исполнительная логика разделены.

## Ключевая идея проекта

Главная идея системы — объединить несколько каналов управления и наблюдения, но не перемешивать их реализацию.

### Единый обработчик команд

Локальный `UART` и сетевые команды работают через один и тот же обработчик моторных команд. Это дает:

- одинаковое поведение независимо от канала управления;
- меньше дублирования логики;
- более простую отладку;
- единый формат состояния двигателя.

### Телеметрия как отдельный слой

Проект не ограничивается "сделать действие". Он еще и показывает состояние:

- через текстовый лог в UART/monitor;
- через JSON по `HTTP`;
- через push-модель по `WebSocket`;
- через отдельные `@telemetry` строки, пригодные для дальнейшего парсинга.

Это особенно полезно для стенда, лабораторной работы и курсовой, потому что можно показать не только код, но и наблюдаемое поведение системы.

## Что именно уже реализовано в текущем коде

### Реализовано точно

- инициализация I2C-шины;
- быстрый scan MPU-адресов `0x68` и `0x69`;
- fallback-диагностика альтернативных пар SDA/SCL при неудаче;
- чтение `WHO_AM_I`;
- чтение сырых значений accel/gyro/temp;
- вычисление физических величин;
- автоматический запуск stepper в режиме `sweep`;
- прием команд через `UART0`;
- REST endpoint для телеметрии;
- REST endpoint для Wi‑Fi статуса;
- REST endpoint для команд stepper;
- WebSocket endpoint;
- периодическая рассылка JSON по WebSocket.

### Есть в коде, но не полностью задействовано

- функция `app_wifi_log_scan_results()` существует, но в текущем коде не вызывается;
- функция построения SSID умеет добавлять MAC-суффикс, но сейчас вызывается с `NULL`, поэтому реально используется только `CONFIG_APP_WIFI_AP_SSID_PREFIX` без суффикса;
- выбор режима приложения через `choice APP_MODE` существует в `Kconfig`, но `app.c` фактически использует `CONFIG_APP_MODE_L293D_TEST` и логику MPU параллельно, то есть проект уже не является строго "однорежимным" в архитектурном смысле.

Эти детали важно зафиксировать в документации, потому что для курсовой полезно показывать не только сильные стороны, но и реальные инженерные компромиссы.

## Сильные стороны архитектуры

- маленький и чистый `main`;
- четкое разделение по компонентам;
- конфигурируемость через `Kconfig`;
- единая точка orchestration в `app.c`;
- общий обработчик команд stepper для разных транспортов;
- отдельный status/snapshot API для интеграции с сетью;
- упор на диагностику и наблюдаемость.

## Ограничения текущего варианта

- нет отдельной RTOS-задачи на каждую подсистему — используется один кооперативный tick-loop;
- JSON собирается вручную через `snprintf`, без полноценной JSON-библиотеки;
- `i2c_bus_read()`/`write()` каждый раз создают и удаляют device handle, что просто, но не оптимально для высокой частоты опроса;
- Web UI живет вне этой части документации;
- проект больше ориентирован на лабораторный стенд, чем на production deployment.

## Почему такая архитектура удобна для курсовой

Она дает материал сразу по нескольким темам:

- архитектура embedded-приложения;
- модульность и слои ответственности;
- работа с периферией и датчиками;
- управление исполнительным устройством;
- взаимодействие микроконтроллера и сети;
- телеметрия и диагностика;
- конфигурирование и сборка в ESP-IDF.

См. также:

- [[02-architecture/Boot and main loop]]
- [[02-architecture/Runtime data flow]]
- [[02-architecture/UART and network dual control]]
- [[02-architecture/WiFi HTTP WebSocket architecture]]



---

## [017] 02-architecture/Telemetry architecture.md

# Telemetry architecture

## Зачем в проекте отдельная телеметрическая архитектура

Проект не ограничивается управлением устройствами. Он также делает состояние системы наблюдаемым. Это критически важно для:

- отладки;
- демонстрации работы стенда;
- построения web-интерфейса;
- подготовки материалов для курсовой.

По сути, телеметрия здесь — это отдельный функциональный слой, а не побочный вывод логов.

## Формы телеметрии в проекте

В текущей реализации используются три формы представления состояния:

- `printf`-строки с префиксом `@telemetry`;
- HTTP JSON-ответ;
- WebSocket JSON-broadcast.

Эти три формы решают разные задачи, но опираются на одни и те же источники состояния.

## 1. Логовая машинно-читаемая телеметрия

Формат `@telemetry {...}` используется как мост между обычным логом и структурированными данными.

Такие строки генерируют:

- `app_emit_system_telemetry()` — состояние системы;
- `app_stepper_emit_telemetry()` — состояние двигателя;
- `app_mpu_emit_telemetry_ready()` — успешная телеметрия MPU;
- `app_mpu_emit_telemetry_error()` — ошибка MPU.

### Почему это полезно

- данные остаются видимыми в UART/monitor;
- при этом они уже пригодны для автоматического парсинга;
- можно легко писать внешний скрипт, который собирает телеметрию из логов;
- удобно использовать как промежуточный формат для будущей аналитики.

## 2. HTTP JSON-телеметрия

Функция `app_net_build_json()` собирает единый снимок системы для web API.

В JSON входят разделы:

- `system`;
- `mpu`;
- `i2c`;
- `stepper`;
- `wifi`.

Это делает `GET /api/telemetry` главным endpoint'ом наблюдения за прошивкой.

## 3. WebSocket push-телеметрия

`app_net_tick()` раз в секунду рассылает тот же JSON всем WebSocket-клиентам.

Это уже push-модель, удобная для:

- dashboards;
- live-интерфейсов;
- непрерывного обновления состояния без ручного polling.

## Источники данных телеметрии

Телеметрия строится не из одного глобального объекта, а из нескольких status/snapshot-структур:

- `app_system_status_t`;
- `app_i2c_status_t`;
- `app_mpu_status_t`;
- `app_stepper_snapshot_t`;
- `app_wifi_status_t`.

Это очень сильное архитектурное решение: каждая подсистема отвечает за свой собственный снимок состояния, а сетевой слой лишь сериализует его.

## Что именно попадает в телеметрию

### System

- `uptime_ms`
- `tick`
- `tick_delay_ms`
- `firmware`
- `app_mode`
- `last_error`

### MPU

- `ready`
- `error`
- `address`
- `whoAmI`
- `model`
- `uptimeLabel`
- `accel`
- `gyro`
- `tempC`

### I2C

- `ready`
- `devices`
- `detectedMpuAddress`
- `lastScanSummary`
- `error`

### Stepper

- `mode`
- `sweepState`
- `delayMs`
- `stepsPerSecond`
- `phaseIndex`
- `totalSteps`
- `coilsEnabled`
- `sweepSteps`
- `uartReady`
- `lastCommand`
- GPIO pins

### Wi‑Fi

- `initialized`
- `apStarted`
- `staAttempted`
- `staConnected`
- `apSsid`
- `apIp`
- `staIp`
- `lastError`

## Частота обновления

В проекте телеметрия не обновляется с одинаковой частотой во всех каналах.

- основной цикл идет с задержкой `5 ms`;
- stepper heartbeat и WebSocket push идут примерно раз в `1 s`;
- MPU/system telemetry в `app.c` тоже идет раз в `1 s`.

Это хороший баланс между наблюдаемостью и нагрузкой.

## Важный инженерный нюанс

JSON собирается вручную через `snprintf`, а не через JSON-библиотеку. Для текущей фиксированной схемы это нормально, но есть ограничения:

- нужно следить за размерами буферов;
- экранирование строк ограничено;
- при росте протокола код станет сложнее сопровождать.

Для лабораторного стенда это допустимо и даже удобно: структура ответа прозрачна и легко читается прямо в коде.

## Почему телеметрия делает проект сильнее

Без телеметрии проект был бы просто демонстрацией управления мотором и чтения датчика. С телеметрией он становится:

- наблюдаемой embedded-системой;
- удобным объектом для интеграции с UI;
- хорошим материалом для описания архитектуры данных в курсовой.

См. также:

- [[03-components/app_net]]
- [[03-components/app_stepper]]
- [[03-components/app_wifi]]
- [[04-functions/app_net_build_json]]



---

## [018] 02-architecture/UART and network dual control.md

# UART and network dual control

## Архитектурная задача

Одна из главных задач проекта — расширить управление шаговым двигателем через сеть, но не потерять уже существующее UART-управление.

Это важный инженерный сценарий: часто в embedded-проектах новый интерфейс нужно добавить поверх старого, не ломая уже работающий способ диагностики и ручного контроля.

## Принцип решения

В проекте выбрано очень удачное решение:

- UART остается внутри `app_stepper.c`;
- сетевой слой не дублирует motor logic;
- наружу добавляется компактный публичный вызов `app_stepper_command_char(char cmd)`;
- и UART, и сеть в итоге сходятся в одном внутреннем обработчике `app_stepper_handle_command(uint8_t cmd)`.

Это означает, что логика интерпретации команд реализована **один раз**.

## Потоки управления

### Путь UART

```text
UART0 -> app_stepper_handle_uart -> app_stepper_handle_command
```

### Путь HTTP

```text
POST /api/command -> app_net_command_handler -> app_stepper_command_char -> app_stepper_handle_command
```

### Путь WebSocket

```text
/ws text frame -> app_net_ws_handler -> app_stepper_command_char -> app_stepper_handle_command
```

Таким образом, три разных транспортных входа приводят к одной и той же исполнительной логике.

## Почему это важно

Такой подход дает сразу несколько преимуществ:

- нет копипасты командной логики;
- поведение одинаково независимо от источника команды;
- проще тестировать и отлаживать;
- при добавлении новой команды ее нужно реализовать в одном месте;
- старый UART-канал продолжает работать как fallback и инструмент отладки.

## Набор команд остается единым

Сохраняется совместимость команд:

- `f`, `r`, `s`, `w`
- `1`, `2`
- `a`, `b`, `c`, `d`
- `+`, `-`
- `z`

То есть оператор, который привык управлять двигателем через UART-символы, фактически может использовать тот же протокол через HTTP/WebSocket.

## Почему это хорошее решение для курсовой

На этом месте можно показать важный инженерный принцип:

> новые интерфейсы не должны дублировать бизнес-логику, они должны переиспользовать существующий domain layer.

В терминах архитектуры проекта:

- `UART` и `HTTP/WebSocket` — это transport layer;
- `app_stepper_handle_command()` — это command execution layer.

## Ограничения текущей схемы

- команды односимвольные, поэтому протокол простой, но не слишком расширяемый;
- нет механизма очередей команд или приоритетов между каналами;
- нет явной арбитрации, если UART и сеть начнут слать команды очень часто одновременно;
- вся обработка выполняется внутри общего tick-loop.

Однако для лабораторного стенда такая схема оптимальна: она проста, надежна и очень понятна при объяснении.

## Практический смысл

В реальной демонстрации это дает очень удобный набор возможностей:

- можно управлять мотором с serial monitor;
- можно управлять через `curl`;
- можно подключить web-клиент;
- при проблемах с сетью UART остается резервным способом контроля.

Именно это делает проект не просто набором отдельных функций, а удобной экспериментальной платформой.



---

## [019] 02-architecture/WiFi HTTP WebSocket architecture.md

# WiFi HTTP WebSocket architecture

## Общая идея

Сетевая архитектура проекта разделена на два компонента:

- `app_wifi.c` — поднимает сетевую среду и хранит Wi‑Fi status;
- `app_net.c` — поднимает HTTP/WebSocket API поверх уже готовой сети.

Это правильное разделение ответственности:

- один слой отвечает за radio/network bringup;
- второй — за прикладной API и транспорт данных.

## Что является опорой архитектуры

Сетевой стек нужен в проекте не просто ради "подключиться к Wi‑Fi", а ради трех конкретных задач:

- дать доступ к телеметрии без UART monitor;
- дать удаленное управление двигателем;
- поддержать будущий внешний web-клиент.

Поэтому архитектура строится не вокруг web-страниц, а вокруг API.

## Последовательность запуска

Фактический порядок работы такой:

1. `app_init()` вызывает `app_wifi_smoke_run()`.
2. Wi‑Fi слой инициализирует `NVS`, `esp_netif`, default event loop.
3. Создаются default netif для `STA` и `AP`.
4. Выбирается режим Wi‑Fi:
	- `WIFI_MODE_AP`, если `CONFIG_APP_WIFI_CONNECT` выключен или SSID пустой;
	- `WIFI_MODE_APSTA`, если включен STA-режим и задан SSID.
5. Конфигурируется SoftAP.
6. При необходимости конфигурируется STA.
7. Вызывается `esp_wifi_start()`.
8. В `app.c` при успешном результате ставится `s_network_ready = true`.
9. Если включен `CONFIG_APP_NET_ENABLE` и сеть считается готовой, вызывается `app_net_start()`.
10. HTTP server начинает принимать запросы.
11. В основном цикле `app_tick()` вызывает `app_net_tick()` для периодической WebSocket-рассылки.

Важно: в текущей конфигурации проекта по умолчанию используется именно режим `AP`, а не `APSTA`, потому что `CONFIG_APP_WIFI_CONNECT` не включен.

## Роль SoftAP в архитектуре

SoftAP — это основной текущий способ доступа к устройству.

Почему это удобно:

- для стенда не нужен внешний роутер;
- ноутбук или телефон можно подключить прямо к ESP;
- проверка API не зависит от UART;
- демонстрация проекта становится автономной.

Это особенно удачно для лабораторной работы и защиты: устройство можно показать без привязки к инфраструктуре аудитории.

## Роль режима `APSTA`

Когда включен `CONFIG_APP_WIFI_CONNECT`, архитектура становится гибче:

- ESP продолжает поднимать собственный AP;
- одновременно может подключаться к внешней Wi‑Fi сети как STA;
- после получения IP появляется `sta_ip`, пригодный для интеграции в общую сеть.

То есть одна и та же прошивка может работать и автономно, и в составе более общей сетевой среды.

## HTTP-часть архитектуры

`app_net.c` регистрирует несколько endpoint'ов:

- `GET /api/telemetry`
- `GET /api/wifi`
- `POST /api/command`
- `OPTIONS /*`
- `GET /ws`

Архитектурно это означает разделение на два паттерна:

- pull-модель через REST;
- push-модель через WebSocket.

### Pull-модель

Подходит для:

- ручной проверки через браузер или `curl`;
- отладки;
- простых клиентов без постоянного соединения.

### Push-модель

Подходит для:

- web-dashboard;
- live-обновления статусов;
- минимизации ручного polling со стороны клиента.

## Как сеть получает данные приложения

`app_net_build_json()` не хранит собственное отдельное состояние всех подсистем, а каждый раз собирает его из источников:

- `app_stepper_get_snapshot()`;
- `app_wifi_get_status()`;
- `app_get_system_status()`;
- `app_mpu_get_status()`;
- `app_get_i2c_status()`.

Это делает сетевой слой очень удобным для сопровождения: он выступает как сериализатор текущего состояния системы.

## WebSocket-рассылка

`app_net_tick()` раз в секунду:

- берет список клиентов HTTP server;
- выбирает только WebSocket-клиентов;
- строит единый JSON;
- ставит асинхронную отправку через очередь работ сервера.

Такая схема хороша тем, что отправка не смешивается с логикой чтения состояния и не требует от клиента постоянно опрашивать REST endpoint.

## CORS и интеграция с внешним UI

API сразу сконфигурирован с CORS-заголовками. Это означает, что отдельный web-клиент может быть запущен с другого origin и всё равно обращаться к устройству.

Для проекта это важный шаг в сторону реальной интеграции фронтенда и embedded-устройства.

## Ограничения текущей сетевой архитектуры

- нет аутентификации и авторизации;
- нет TLS;
- JSON формируется вручную;
- нет статической раздачи frontend-ресурсов из этого модуля;
- нет versioned API.

Но для лабораторного стенда этого более чем достаточно: архитектура уже показывает взаимодействие прошивки, сети и внешнего клиента на практическом уровне.

См. также:

- [[03-components/app_wifi]]
- [[03-components/app_net]]
- [[06-operations/Runtime WiFi verification without UART]]
- [[06-operations/API examples]]



---

## [020] 03-components/app component.md

# app component

`components/app` — это главный прикладной компонент проекта. Именно он делает из набора отдельных модулей одну работающую прошивку.

## Что входит в компонент

Содержимое компонента:

- `src/app.c` — общий координатор;
- `src/app_wifi.c` — Wi‑Fi bringup и статусы;
- `src/app_net.c` — HTTP/WebSocket API;
- `src/app_stepper.c` — управление шаговым двигателем;
- `src/app_mpu_pretty.c` — MPU telemetry/log formatting;
- `include/*.h` — публичный интерфейс для остальных частей проекта.

С точки зрения сборки компонент объявлен в `components/app/CMakeLists.txt` и явно зависит от:

- `i2c_bus`;
- `mpu9250`;
- `esp_driver_gpio`;
- `esp_driver_uart`;
- `esp_wifi`;
- `esp_event`;
- `esp_http_server`;
- `esp_netif`;
- `nvs_flash`.

Это удобно для пояснения архитектуры: `app` — не низкоуровневый драйвер, а агрегирующий бизнес-слой прошивки.

## Главная роль компонента

У компонента три основные задачи:

1. скрыть детали ESP-IDF от `main`;
2. связать между собой сенсоры, управление двигателем и сеть;
3. дать единый жизненный цикл приложения.

Именно поэтому наружу экспортируются простые функции:

- `app_init()`;
- `app_tick()`;
- `app_tick_delay_ms()`.

## Что делает `app.c`

Файл `app.c` — центральная orchestration-точка проекта.

Он отвечает за:

- настройку уровней логирования;
- запуск I2C;
- первичный scan шины;
- проверку наличия MPU;
- запуск Wi‑Fi при включенном `CONFIG_APP_WIFI_SMOKE`;
- запуск stepper subsystem при `CONFIG_APP_MODE_L293D_TEST`;
- запуск сетевого API при `CONFIG_APP_NET_ENABLE` и готовой сети;
- периодическую генерацию system telemetry;
- вызов периодического опроса MPU.

Кроме того, `app.c` хранит два важных публичных состояния:

- `app_system_status_t` — общесистемное состояние;
- `app_i2c_status_t` — сводка по I2C и обнаружению MPU.

## Почему это хороший центр композиции

`app.c` почти не реализует аппаратную логику сам, но знает, в каком порядке запускать другие подсистемы. Это правильное разделение ответственности:

- модуль знает **как работать**;
- `app.c` знает **когда и зачем его запускать**.

Такой подход:

- уменьшает связность между модулями;
- облегчает чтение проекта;
- упрощает расширение архитектуры;
- делает объяснение на защите намного проще.

## Какие публичные данные компонент отдает другим слоям

Через `app.h` наружу доступны:

- `app_get_system_status()`;
- `app_get_i2c_status()`;
- `app_set_system_error()`.

Эти функции используются, в частности, сетевым слоем для сборки JSON-ответов.

## Важный инженерный нюанс

Компонент `app` здесь не равен одной функции или одному модулю. Это, по сути, "прикладная платформа" прошивки.

Внутри него объединены сразу три типа логики:

- orchestration;
- domain logic;
- integration с сетевыми и аппаратными подсистемами.

Для лабораторного проекта это разумный компромисс: проект остается компактным, но структура уже похожа на взрослое многомодульное приложение.

## Что особенно полезно для курсовой

На примере `components/app` удобно показать:

- принцип модульной архитектуры;
- разделение ответственности;
- единый жизненный цикл встроенного приложения;
- связь между конфигурацией и составом функциональности;
- построение API поверх внутренних статусов.

См. также:

- [[04-functions/app_init]]
- [[04-functions/app_tick]]
- [[02-architecture/System overview]]
- [[02-architecture/Runtime data flow]]



---

## [021] 03-components/app_mpu_pretty.md

# app_mpu_pretty

Файл: `components/app/src/app_mpu_pretty.c`.

Назначение:

- обнаружить MPU;
- вывести WHO_AM_I;
- прочитать конфиги gyro/accel scale;
- периодически читать 14 байт raw telemetry;
- перевести raw accelerometer в `g`;
- перевести raw gyroscope в `dps`;
- перевести raw temperature в Celsius;
- напечатать красивую строку и JSON-подобную телеметрию.

Главное состояние:

- `s_mpu.addr`
- `s_mpu.whoami`
- `s_mpu.accel_lsb_per_g`
- `s_mpu.gyro_lsb_per_dps`
- `s_mpu.ready`

Главные функции:

- [[04-functions/app_mpu_pretty_init]]
- [[04-functions/app_mpu_pretty_log_line]]
- [[04-functions/app_mpu_i16be]]
- [[04-functions/app_mpu_accel_lsb_per_g]]
- [[04-functions/app_mpu_gyro_lsb_per_dps]]



---

## [022] 03-components/app_net.md

# app_net

Файл: `components/app/src/app_net.c`.

## Назначение компонента

`app_net` — сетевой фасад прошивки. Он дает внешнему клиенту доступ к состоянию системы и к управлению шаговым двигателем.

Основные задачи:

- поднять встроенный HTTP server из ESP-IDF;
- зарегистрировать REST endpoints;
- поднять WebSocket endpoint;
- собрать единый JSON состояния из нескольких подсистем;
- передать команду управления stepper через общий публичный API;
- регулярно пушить телеметрию всем WebSocket-клиентам.

## Почему этот модуль важен архитектурно

`app_net` не содержит бизнес-логики двигателя и не работает напрямую с железом. Он является transport/integration-слоем между внешним клиентом и внутренними модулями прошивки.

Это хороший признак правильной модульности: сеть отвечает за транспорт, а не за управление GPIO или вычисление фаз.

## Экспортируемые endpoints

### `GET /api/telemetry`

Возвращает единый JSON-объект, включающий:

- `system`;
- `mpu`;
- `i2c`;
- `stepper`;
- `wifi`.

Это главный endpoint для мониторинга состояния всей прошивки.

### `GET /api/wifi`

Возвращает более короткий JSON только по Wi‑Fi статусу.

### `POST /api/command`

Принимает команду для stepper. В текущей реализации команда извлекается очень просто:

- либо из JSON-поля `"command"`;
- либо как первый небесполезный символ в body.

Пример полезной нагрузки:

```json
{"command":"f"}
```

или даже просто:

```text
f
```

### `GET /ws`

WebSocket endpoint:

- принимает команды от клиента;
- после приема сразу отдает актуальный JSON-снимок;
- дополнительно получает периодические push-обновления из `app_net_tick()`.

### `OPTIONS /*`

Нужен для CORS preflight. Это особенно важно, если фронтенд запускается не с того же origin.

## Как формируется JSON

Функция `app_net_build_json()` собирает данные не из внутренних статических переменных других модулей, а через их публичные API:

- `app_stepper_get_snapshot()`;
- `app_wifi_get_status()`;
- `app_get_system_status()`;
- `app_mpu_get_status()`;
- `app_get_i2c_status()`.

Такой подход дает сразу несколько плюсов:

- модульность;
- меньшую связность;
- простую сериализацию;
- понятный контракт между подсистемами.

## Формат данных

JSON собирается вручную через `snprintf`. Это просто и прозрачно для небольшого проекта, но важно помнить ограничения:

- нужен контроль размеров буферов;
- нет автоматического escaping сложных строк;
- при росте схемы ответов код станет менее удобным.

Для текущего лабораторного масштаба это приемлемый компромисс.

## Команды управления двигателем

Сетевой слой не знает ничего про фазы L293D. Он оперирует только символом команды:

- `f` — вперед;
- `r` — назад;
- `s` — стоп;
- `w` — sweep;
- `1`, `2` — одиночные шаги;
- `a`, `b`, `c`, `d` — фиксация фазы;
- `+`, `-` — изменение скорости;
- `z` — release coils.

После извлечения символа вызывается `app_stepper_command_char(cmd)`.

## Работа WebSocket push-модели

Раз в секунду `app_net_tick()`:

1. проверяет, что сервер уже запущен;
2. ограничивает частоту отправки через `s_last_push_ms`;
3. получает список клиентских сокетов;
4. фильтрует только WebSocket-клиентов;
5. ставит асинхронную отправку через `httpd_queue_work()`.

Отдельная асинхронная функция `app_net_ws_send_work()` нужна, чтобы не отправлять frame прямо из случайного контекста.

## Внутреннее состояние

- `s_server` — handle HTTP server;
- `s_last_push_ms` — timestamp последней рассылки;
- `app_net_ws_msg_t` — временная структура для queued WS-передачи.

## CORS и интеграция с фронтендом

Функция `app_net_set_cors()` всегда выставляет заголовки:

- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET,POST,OPTIONS`
- `Access-Control-Allow-Headers: Content-Type`

Это значит, что API изначально подготовлен для взаимодействия с внешним web-клиентом без жесткой same-origin привязки.

## Сильные стороны реализации

- компактный API;
- единый JSON состояния;
- WebSocket push для живого интерфейса;
- отсутствие дублирования логики stepper;
- CORS уже учтен;
- использование публичных snapshot/status API вместо прямого доступа к чужому состоянию.

## Ограничения текущего решения

- JSON строится вручную;
- нет аутентификации;
- нет маршрутизации статических файлов UI в этом модуле;
- нет сложной схемы команд или подтверждений выполнения;
- нет отдельного слоя versioning для API.

Для лабораторного проекта это нормально: модуль уже демонстрирует практическую сетевую интеграцию, но не перегружен enterprise-логикой.

Главные функции:

- [[04-functions/app_net_start]]
- [[04-functions/app_net_tick]]
- [[04-functions/app_net_build_json]]
- [[04-functions/app_net_command_handler]]
- [[04-functions/app_net_ws_handler]]



---

## [023] 03-components/app_stepper.md

# app_stepper

Файл: `components/app/src/app_stepper.c`.

## Назначение компонента

`app_stepper` реализует управление шаговым двигателем через драйвер `L293D`. Это один из центральных модулей проекта, потому что именно он связывает физическое исполнительное устройство с двумя каналами управления:

- локальным через `UART0`;
- удаленным через `HTTP/WebSocket`.

## Что делает модуль

Основные обязанности:

- настроить GPIO, подключенные к `L293D`;
- при необходимости настроить activity LED;
- инициализировать UART для приема символьных команд;
- хранить внутреннее состояние двигателя;
- реализовать несколько режимов движения;
- управлять фазами обмоток;
- публиковать состояние наружу;
- выдавать текстовую и машинно-читаемую телеметрию.

## Внутренние структуры

### `app_stepper_phase_t`

Описывает одну фазу возбуждения:

- уровни `in1..in4`;
- человекочитаемую метку.

Массив `s_phases` содержит 4 фазы:

- phase A;
- phase B;
- phase C;
- phase D.

Это компактная таблица управления, через которую строятся forward/reverse шаги.

### `app_stepper_state_t`

Хранит текущее runtime-состояние:

- текущий режим;
- состояние sweep-машины;
- индекс фазы;
- задержку между шагами;
- время последнего шага;
- счетчики шагов;
- готовность UART;
- состояние катушек;
- состояние светодиода;
- последнюю команду.

## Режимы работы

Поддерживаются режимы:

- `stop` — двигатель остановлен, обмотки освобождены;
- `forward` — непрерывное движение вперед;
- `reverse` — непрерывное движение назад;
- `sweep` — качание вперед-назад с паузами на краях.

Режим `sweep` особенно удобен для лабораторной демонстрации: система сразу показывает, что двигатель жив, а логика периодического tick работает.

## Символьный интерфейс команд

Модуль принимает компактные однобайтные команды.

Основные команды:

- `h` — вывести справку;
- `p` — вывести статус;
- `s` — стоп;
- `f` — движение вперед;
- `r` — движение назад;
- `w` — режим sweep;
- `1` — один шаг вперед;
- `2` — один шаг назад;
- `a`, `b`, `c`, `d` — удержание конкретной фазы;
- `+` или `=` — ускорение;
- `-` или `_` — замедление;
- `z` — release coils.

Это очень удобный интерфейс и для UART-консоли, и для простого web-клиента.

## Защита от дребезга команд

В коде есть `APP_STEPPER_DUPLICATE_CMD_GUARD_MS = 150 ms`.

Если одна и та же команда приходит слишком быстро повторно, она игнорируется. Это снижает вероятность лишних переключений режима из-за повторной отправки символов или нестабильного клиента.

## Как выполняется физический шаг

Для шага вперед:

- берется текущая фаза из `s_phases[s_stepper.phase_index]`;
- вызывается `app_stepper_apply_phase()`;
- индекс фазы циклически увеличивается.

Для шага назад:

- индекс предварительно уменьшается по кругу;
- затем активируется соответствующая фаза.

В обоих случаях увеличивается `total_steps`.

## Роль `tick`

`app_stepper_tick()` — сердце модуля. В каждом цикле она:

- читает UART, если он готов;
- раз в секунду отправляет heartbeat-telemetry;
- в зависимости от текущего режима решает, пора ли делать следующий шаг;
- обслуживает паузы на краях режима sweep.

Это не потоковая блокирующая логика, а кооперативная state machine. Такой подход хорошо согласуется с общим циклом `app_tick()`.

## Инициализация

`app_stepper_init()` выполняет:

1. настройку GPIO;
2. настройку LED, если он включен конфигом;
3. release катушек в безопасное состояние;
4. настройку UART;
5. вывод параметров в лог;
6. печать списка команд;
7. автоматический переход в режим `sweep`.

То есть после старта двигатель уже может показать демонстрационное поведение без дополнительных внешних команд.

## Публичный API

Сетевой слой использует два ключевых вызова:

- `app_stepper_command_char(char cmd)` — передать символ команды;
- `app_stepper_get_snapshot(app_stepper_snapshot_t *snapshot)` — получить снимок состояния.

Это хорошее проектное решение, потому что:

- HTTP/WebSocket не зависят от внутренней реализации state machine;
- можно менять транспорт, не меняя моторную логику;
- состояние двигателя легко сериализовать в JSON.

## Телеметрия

Модуль генерирует `@telemetry`-строки с полями:

- `mode`;
- `sweep_state`;
- `step_delay_ms`;
- `steps_per_second`;
- `phase_index`;
- `total_steps`;
- `coils_enabled`;
- `sweep_steps`;
- `uart_ready`;
- `last_command`;
- GPIO-пины.

Это делает модуль не "черным ящиком", а наблюдаемой системой.

## Ограничения и инженерные компромиссы

- используется простой фазовый шаблон из 4 состояний;
- нет профилей ускорения/торможения;
- нет контроля реального положения ротора по энкодеру;
- используется один общий tick-loop, а не отдельная RTOS-задача двигателя;
- команды односимвольные, что просто, но ограничивает расширяемость протокола.

Для учебной лабораторной прошивки это хороший баланс между простотой и наглядностью.

Главные функции:

- [[04-functions/app_stepper_init]]
- [[04-functions/app_stepper_tick]]
- [[04-functions/app_stepper_handle_command]]
- [[04-functions/app_stepper_command_char]]
- [[04-functions/app_stepper_get_snapshot]]
- [[04-functions/app_stepper_apply_phase]]
- [[04-functions/app_stepper_release]]



---

## [024] 03-components/app_wifi.md

# app_wifi

Файл: `components/app/src/app_wifi.c`.

## Назначение компонента

`app_wifi` поднимает сетевую подсистему и хранит компактное состояние Wi‑Fi, которое потом используют другие части прошивки.

Основные задачи файла:

- инициализировать `NVS`;
- инициализировать `esp_netif` и default event loop;
- создать интерфейсы `STA` и `AP`;
- запустить Wi‑Fi stack;
- поднять SoftAP;
- при включенном `CONFIG_APP_WIFI_CONNECT` настроить подключение к внешней сети;
- обновлять статус подключения;
- отдавать снимок состояния наружу через `app_wifi_get_status()`.

## Что реально делает текущая реализация

Важно отделять реальный код от запланированного поведения.

### Реально выполняется сейчас

- запускается SoftAP;
- выбирается `WIFI_MODE_AP` или `WIFI_MODE_APSTA` в зависимости от `CONFIG_APP_WIFI_CONNECT` и наличия SSID;
- назначается SSID точки доступа из `CONFIG_APP_WIFI_AP_SSID_PREFIX`;
- при включенном STA-режиме задаются учетные данные для подключения к внешней сети;
- регистрируются обработчики событий Wi‑Fi и IP;
- обновляются поля `ap_started`, `sta_attempted`, `sta_connected`, `ap_ip`, `sta_ip`.

### Что в коде есть, но сейчас фактически не используется

- функция `app_wifi_log_scan_results()` реализована, но не вызывается;
- функция `app_wifi_build_ap_ssid()` умеет строить SSID с MAC-суффиксом, однако в текущем коде вызывается как `app_wifi_build_ap_ssid(..., NULL)`, поэтому в реальности используется просто строка-префикс без MAC-суффикса.

Это стоит прямо фиксировать, чтобы документация не расходилась с проектом.

## Внутреннее состояние

Ключевые static-переменные:

- `s_sta_netif` — интерфейс станции;
- `s_ap_netif` — интерфейс точки доступа;
- `s_wifi_started` — защита от повторного запуска;
- `s_status` — структура `app_wifi_status_t`, которую видят остальные модули.

Структура `app_wifi_status_t` содержит:

- `initialized` — прошла ли базовая инициализация Wi‑Fi;
- `ap_started` — запущена ли точка доступа;
- `sta_attempted` — пыталась ли прошивка подключиться как клиент;
- `sta_connected` — подключилась ли она как клиент;
- `ap_ssid` — SSID точки доступа;
- `ap_ip` — IP точки доступа;
- `sta_ip` — IP клиента в режиме STA;
- `last_error` — последний `esp_err_t`.

## Последовательность запуска

Функция `app_wifi_smoke_run()` делает следующее:

1. Проверяет, доступен ли Wi‑Fi stack для текущей конфигурации ESP-IDF.
2. Защищается от повторного запуска через `s_wifi_started`.
3. Инициализирует `NVS`.
4. Инициализирует `esp_netif`.
5. Создает event loop.
6. Создает default netif для `STA` и `AP`.
7. Вызывает `esp_wifi_init()`.
8. Регистрирует общие обработчики событий.
9. Выбирает режим `AP` или `APSTA`.
10. Конфигурирует SoftAP.
11. При необходимости конфигурирует STA.
12. Запускает Wi‑Fi и отключает power save через `esp_wifi_set_ps(WIFI_PS_NONE)`.
13. Обновляет статус и возвращает `ESP_OK`.

## Работа событийной модели

В проекте есть два уровня обработки событий:

- `app_wifi_event_handler_common()` — общая часть;
- `app_wifi_event_handler()` — дополнительные реакции для STA-режима.

Это разделение удобно, потому что AP-события нужны всегда, а STA-логика включается условно через `CONFIG_APP_WIFI_CONNECT`.

Типовые события:

- `WIFI_EVENT_AP_START` → точка доступа поднята;
- `WIFI_EVENT_AP_STOP` → точка доступа остановлена;
- `WIFI_EVENT_STA_START` → можно инициировать подключение клиента;
- `WIFI_EVENT_STA_DISCONNECTED` → фиксируется ошибка и при необходимости выполняется retry;
- `IP_EVENT_STA_GOT_IP` → клиент успешно получил IP;
- `IP_EVENT_AP_STAIPASSIGNED` → обновляется IP-информация AP.

## Как компонент используется остальной системой

- `app.c` вызывает `app_wifi_smoke_run()` при старте;
- `app_net.c` читает `app_wifi_get_status()` при формировании JSON;
- логика запуска API зависит от результата инициализации Wi‑Fi.

То есть `app_wifi` — не просто драйвер, а поставщик сетевого статуса для других модулей.

## Ограничения и особенности

- SoftAP — основной режим работы текущей конфигурации;
- scan AP уже реализован, но не встроен в runtime-цепочку;
- имя точки доступа пока не уникализируется через MAC, хотя функция для этого заготовлена;
- код написан как bringup/smoke-уровень, а не как полнофункциональный network manager.

## Что можно использовать в курсовой

На этом модуле удобно показать:

- инициализацию сетевой подсистемы ESP-IDF;
- использование event-driven модели;
- построение собственного слоя статуса над SDK;
- различие между режимами `AP`, `STA` и `APSTA`;
- роль `Kconfig` в управлении составом функциональности.

Главные функции:

- [[04-functions/app_wifi_smoke_run]]
- [[04-functions/app_wifi_get_status]]
- [[04-functions/app_wifi_event_handler_common]]
- [[04-functions/app_wifi_build_ap_ssid]]
- [[04-functions/app_wifi_nvs_init_once]]



---

## [025] 03-components/i2c_bus.md

# i2c_bus

Файл: `components/i2c_bus/src/i2c_bus.c`.

## Назначение компонента

`i2c_bus` — это низкоуровневая обертка над API `i2c_master` из ESP-IDF. Компонент дает остальной прошивке простой и единый способ:

- поднять I2C master bus;
- проверить состояние линий;
- выполнить scan;
- пробовать конкретный адрес;
- читать и писать регистры устройств.

## Почему этот модуль важен

Без него код работы с MPU пришлось бы размазывать по нескольким файлам. Здесь же I2C вынесен в отдельный reusable-слой, что делает архитектуру чище.

## Инициализация шины

`i2c_bus_init()` выполняет несколько полезных шагов:

1. проверяет, не инициализирована ли шина уже;
2. при включенном `CONFIG_I2C_BUS_SELFTEST` запускает self-test линий;
3. читает idle levels на SDA/SCL до подключения периферии I2C;
4. предупреждает, если какая-то линия удерживается в `0`;
5. создает master bus через `i2c_new_master_bus()`;
6. логирует итоговую конфигурацию.

Этот подход полезен для реальной отладки железа: можно рано заметить проблемы с питанием, pull-up резисторами или перепутанными линиями.

## Scan шины

`i2c_bus_scan()` имеет двухступенчатую стратегию:

- сначала быстрый probe только адресов `0x68` и `0x69`;
- затем, если включен `CONFIG_I2C_BUS_SCAN_FULL`, полный перебор диапазона `0x03..0x77`.

Это разумный компромисс:

- для основного сценария с MPU не тратится лишнее время;
- при необходимости можно включить полную диагностику.

Компонент дополнительно считает:

- количество найденных устройств;
- число timeout;
- число остальных ошибок.

## Работа с регистрами

### `i2c_bus_read()`

Выполняет типичную операцию register read:

- открывает временный device handle;
- отправляет адрес регистра;
- читает `out_len` байт ответа;
- удаляет handle устройства.

### `i2c_bus_write()`

Формирует буфер вида:

`[reg][payload...]`

После этого выполняет передачу и освобождает временный device handle.

## Важная особенность реализации

`i2c_bus_read()` и `i2c_bus_write()` каждый раз создают device handle через `i2c_bus_open_device()` и потом удаляют его через `i2c_master_bus_rm_device()`.

Плюсы такого решения:

- простая логика;
- не нужно хранить таблицу открытых устройств;
- меньше риска рассинхронизации состояния устройств в маленьком проекте.

Минусы:

- дополнительный overhead на каждом чтении/записи;
- не лучший выбор для высокочастотного polling в production-сценарии.

Для текущего лабораторного проекта этот компромисс выглядит оправданным.

## Диагностика уровней линий

В модуле есть вспомогательные функции:

- `i2c_bus_read_lines()`;
- `i2c_bus_log_lines()`;
- `i2c_bus_selfcheck_gpio()`.

Они нужны не для прикладной логики, а для инженерной диагностики. Это сильная сторона проекта: разработчик сразу получает больше информации о том, что происходит на физическом уровне шины.

## Ограничения и ограничения буферов

В `i2c_bus_write()` есть маленький статический буфер `uint8_t buf[1 + 16]`, поэтому запись ограничена `16` байтами полезных данных за одну операцию. Для конфигурационных регистров MPU этого достаточно, но для более общих сценариев это нужно учитывать.

## Связь с другими компонентами

- `app.c` использует `i2c_bus_init()`, `i2c_bus_scan()`, `i2c_bus_deinit()`;
- `mpu9250.c` использует `i2c_bus_probe_addr()`, `i2c_bus_read()`, `i2c_bus_write()`;
- `app_mpu_pretty.c` использует `i2c_bus_read()` и `i2c_bus_write()` для чтения регистров MPU.

Именно поэтому `i2c_bus` можно рассматривать как базовый инфраструктурный слой сенсорной подсистемы.

Главные функции:

- [[04-functions/i2c_bus_init]]
- [[04-functions/i2c_bus_deinit]]
- [[04-functions/i2c_bus_scan]]
- [[04-functions/i2c_bus_probe_addr]]
- [[04-functions/i2c_bus_read]]
- [[04-functions/i2c_bus_write]]



---

## [026] 03-components/i2c_bus_diag.md

# i2c_bus_diag

Файл: `components/i2c_bus/src/i2c_bus_diag.c`.

Назначение:

- помочь найти правильные пары SDA/SCL, если MPU не найден;
- попробовать набор типичных GPIO пар;
- для каждой пары создать временный I2C bus;
- проверить адреса `0x68` и `0x69`;
- удалить временный bus.

Это диагностический код. Он вызывается из `app_mpu_whoami_check()`, если обычный поиск MPU не сработал.

Главные функции:

- [[04-functions/i2c_bus_diag_sweep_mpu_pairs]]
- [[04-functions/i2c_bus_diag_probe_pair]]



---

## [027] 03-components/mpu9250.md

# mpu9250

Файл: `components/mpu9250/src/mpu9250.c`.

## Назначение компонента

`mpu9250` — это компактный вспомогательный модуль для базовой работы с датчиком семейства MPU. Его задача — не заменить полноценный драйвер, а закрыть минимально необходимый функционал для проекта:

- найти устройство на шине;
- прочитать `WHO_AM_I`;
- интерпретировать код устройства в человекочитаемое имя.

## Почему модуль выделен отдельно

Хотя функций здесь немного, вынесение в отдельный компонент полезно:

- логика поиска датчика отделена от I2C-слоя;
- `app_mpu_pretty.c` не обязан знать детали начального probe;
- проект получает чистую прослойку "sensor discovery".

## Что делает каждая функция

### `mpu9250_probe_addr()`

Последовательно проверяет адреса:

- `0x68`;
- `0x69`.

Если устройство отвечает, адрес возвращается через `out_addr`.

Это соответствует типовой схеме MPU, где младший бит адреса может зависеть от состояния `AD0`.

### `mpu9250_read_whoami()`

Перед чтением `WHO_AM_I` выполняется запись `0x00` в `PWR_MGMT_1`, то есть датчик пробуждается из sleep-состояния. После этого читается регистр `0x75`.

Это очень практичный шаг: модуль сразу учитывает типовую особенность MPU, а не перекладывает ее на вызывающий код.

### `mpu9250_probe_and_read_whoami()`

Комбинированная функция:

1. найти адрес;
2. прочитать `WHO_AM_I`.

Именно этот вызов чаще всего используется прикладным слоем.

### `mpu9250_whoami_name()`

Возвращает строковое описание модели:

- `0x70` → `MPU-6500`;
- `0x71` → `MPU-9250`;
- `0x73` → `MPU-9255/variant`;
- иначе → `unknown/clone`.

Это полезно для логов и для телеметрии, особенно если на стенде встречаются совместимые модули или клоны.

## Что модуль сознательно НЕ делает

Он не умеет:

- настраивать DLPF;
- задавать частоты выборки;
- включать/отключать оси;
- читать fifo;
- работать с магнитометром;
- выполнять калибровку.

То есть это именно helper-слой для обнаружения и базовой идентификации датчика.

## Связь с другими компонентами

- использует `i2c_bus` как транспорт;
- вызывается из `app.c` для первичной проверки наличия MPU;
- вызывается из `app_mpu_pretty_init()` для ленивой инициализации telemetry-слоя.

## Почему это полезно для курсовой

На этом модуле удобно показать идею минимального driver-like abstraction:

- низкий слой (`i2c_bus`) умеет только транспорт;
- слой `mpu9250` знает про конкретный девайс и его идентификатор;
- верхний слой `app_mpu_pretty` уже строит телеметрию и форматирование.

Это хороший пример многоуровневой декомпозиции даже в небольшом embedded-проекте.

Главные функции:

- [[04-functions/mpu9250_probe_addr]]
- [[04-functions/mpu9250_read_whoami]]
- [[04-functions/mpu9250_probe_and_read_whoami]]
- [[04-functions/mpu9250_whoami_name]]



---

## [028] 04-functions/app_emit_system_telemetry.md

# app_emit_system_telemetry

Исходник: `components/app/src/app.c`.

`app_emit_system_telemetry()` печатает системную telemetry строку.

Поля:

- `kind: system`;
- `uptime_ms`;
- `tick`;
- `tick_delay_ms`;
- `firmware`;
- `app_mode`.

Функция используется из `app_tick()` при включенном `CONFIG_APP_TICK_LOG`.

Это UART/log telemetry, не HTTP API.



---

## [029] 04-functions/app_init.md

# app_init

Исходник: `components/app/src/app.c`.

`app_init()` - центральная функция разовой инициализации проекта.

Порядок действий:

- настраивает уровни логирования;
- печатает блок `APP INITIALIZATION`;
- вызывает `i2c_bus_init()`;
- вызывает `i2c_bus_scan()`;
- вызывает `app_mpu_whoami_check()`;
- если включен `CONFIG_APP_WIFI_SMOKE`, вызывает `app_wifi_smoke_run()`;
- если `app_wifi_smoke_run()` вернул `ESP_OK`, ставит `s_network_ready = true`;
- если включен `CONFIG_APP_MODE_L293D_TEST`, вызывает `app_stepper_init()`;
- если включен `CONFIG_APP_NET_ENABLE` и сеть готова, вызывает `app_net_start()`.

Важная деталь: сетевой сервер не стартует сам по себе. Он стартует только после успешного Wi-Fi bringup.

Еще одна важная деталь: если `i2c_bus_init()` завершается ошибкой, `app_init()` логирует проблему и завершает работу раньше, без продолжения общей цепочки инициализации.

Связи:

- [[04-functions/i2c_bus_init]]
- [[04-functions/i2c_bus_scan]]
- [[04-functions/app_wifi_smoke_run]]
- [[04-functions/app_stepper_init]]
- [[04-functions/app_net_start]]



---

## [030] 04-functions/app_log_color_block.md

# app_log_color_block

Исходник: `components/app/src/app.c`.

`app_log_color_block()` печатает визуальный разделитель в логах.

Аргументы:

- `label`: подпись блока;
- `color`: ANSI escape-последовательность цвета.

Что делает:

- печатает линию `----------------------------------------`;
- если label не пустой, печатает подпись;
- печатает вторую линию;
- сбрасывает цвет через `APP_LOG_COLOR_RESET`.

Функция не влияет на логику устройства. Она нужна, чтобы boot log было легче читать в serial monitor.



---

## [031] 04-functions/app_main.md

# app_main

Исходник: `main/main.c`.

`app_main()` - стандартная точка входа приложения в ESP-IDF. В обычном C для ПК мы ожидаем `main()`, но в ESP-IDF фреймворк сам стартует систему и вызывает `app_main()`.

## Роль в архитектуре

Это верхняя точка прикладного жизненного цикла. Она намеренно очень маленькая: весь смысл функции в том, чтобы передать управление orchestration-слою и дальше не захламлять entry point деталями проекта.

Что делает функция:

- пишет лог `boot`;
- вызывает `app_init()`;
- входит в бесконечный цикл;
- на каждой итерации вызывает `app_tick()`;
- делает задержку через `vTaskDelay(pdMS_TO_TICKS(app_tick_delay_ms()))`.

Почему так:

- микроконтроллерная прошивка не должна завершаться;
- работа приложения разбита на маленькие периодические шаги;
- Wi-Fi и HTTP server живут в задачах ESP-IDF, а прикладной слой обновляет свое состояние в `app_tick()`.

## Почему это хороший стиль

Такой `app_main()` удобен сразу по нескольким причинам:

- его легко объяснить на защите;
- он не зависит от деталей подсистем;
- вся прикладная логика живет в `components/app`;
- структура проекта напоминает взрослое модульное приложение, а не один длинный `main.c`.

## Практический вывод

Если нужно понять весь runtime проекта, начинать чтение кода стоит именно отсюда, а потом сразу переходить в `app_init()` и `app_tick()`.

Связи:

- [[04-functions/app_init]]
- [[04-functions/app_tick]]
- [[04-functions/app_tick_delay_ms]]



---

## [032] 04-functions/app_mpu_accel_lsb_per_g.md

# app_mpu_accel_lsb_per_g

Исходник: `components/app/src/app_mpu_pretty.c`.

`app_mpu_accel_lsb_per_g()` переводит `ACCEL_CONFIG` в scale factor.

Варианты:

- `0`: `16384.0f`, диапазон `+/-2g`;
- `1`: `8192.0f`, диапазон `+/-4g`;
- `2`: `4096.0f`, диапазон `+/-8g`;
- `3`: `2048.0f`, диапазон `+/-16g`.

Значение нужно, чтобы перевести raw accelerometer counts в `g`.



---

## [033] 04-functions/app_mpu_emit_telemetry_error.md

# app_mpu_emit_telemetry_error

Исходник: `components/app/src/app_mpu_pretty.c`.

`app_mpu_emit_telemetry_error()` печатает telemetry строку ошибки MPU.

Формат:

```text
@telemetry {"kind":"mpu","ready":false,"error":"..."}
```

Ошибка переводится в строку через `esp_err_to_name(err)`.



---

## [034] 04-functions/app_mpu_emit_telemetry_ready.md

# app_mpu_emit_telemetry_ready

Исходник: `components/app/src/app_mpu_pretty.c`.

`app_mpu_emit_telemetry_ready()` печатает telemetry строку, когда MPU успешно прочитан.

Поля:

- `kind: mpu`;
- `ready: true`;
- `address`;
- `whoami`;
- `model`;
- `uptime`;
- `tick`;
- `accel.x_g/y_g/z_g`;
- `gyro.x_dps/y_dps/z_dps`;
- `temp_c`.

Эта telemetry идет в stdout/UART log, а не в HTTP API.



---

## [035] 04-functions/app_mpu_gyro_lsb_per_dps.md

# app_mpu_gyro_lsb_per_dps

Исходник: `components/app/src/app_mpu_pretty.c`.

`app_mpu_gyro_lsb_per_dps()` переводит `GYRO_CONFIG` в scale factor.

Варианты:

- `0`: `131.0f`, диапазон `+/-250 dps`;
- `1`: `65.5f`, диапазон `+/-500 dps`;
- `2`: `32.8f`, диапазон `+/-1000 dps`;
- `3`: `16.4f`, диапазон `+/-2000 dps`.

Значение нужно, чтобы перевести raw gyro counts в градусы в секунду.



---

## [036] 04-functions/app_mpu_i16be.md

# app_mpu_i16be

Исходник: `components/app/src/app_mpu_pretty.c`.

`app_mpu_i16be()` собирает signed 16-bit число из двух байт big-endian.

Формула:

```c
(int16_t)(((uint16_t)hi << 8) | lo)
```

MPU registers хранят 16-bit значения как старший байт, затем младший байт. Поэтому функция нужна для raw accelerometer/gyro/temperature.



---

## [037] 04-functions/app_mpu_pretty_init.md

# app_mpu_pretty_init

Исходник: `components/app/src/app_mpu_pretty.c`.

## Назначение

`app_mpu_pretty_init()` лениво подготавливает подсистему телеметрии MPU. Это не просто "init ради init", а мост между:

- базовым обнаружением устройства (`mpu9250_*`);
- низкоуровневым обменом по I2C (`i2c_bus_*`);
- дальнейшим преобразованием сырых данных в физические величины.

Функция вызывается из `app_mpu_pretty_log_line()`, то есть инициализация происходит только тогда, когда реально нужна телеметрия.

## Почему используется ленивая инициализация

Такой подход дает несколько плюсов:

- не нужно поднимать сенсорную подсистему отдельно в `app_init()`;
- сокращается связность между общим lifecycle и подсистемой MPU;
- если телеметрия не запрашивается, дополнительной работы не выполняется;
- при ошибке инициализации ее можно сразу вернуть вызывающему коду, который уже готов красиво отлогировать проблему.

## Последовательность работы

Функция выполняет следующие шаги.

### 1. Проверка кэша готовности

Если `s_mpu.ready == true`, функция сразу возвращает `ESP_OK`.

Это означает, что повторная инициализация не требуется и параметры устройства уже известны.

### 2. Поиск устройства и чтение `WHO_AM_I`

Вызов:

```c
esp_err_t err = mpu9250_probe_and_read_whoami(&s_mpu.addr, &who);
```

Что происходит внутри этого вызова:

- перебираются адреса `0x68` и `0x69`;
- при успешном probe читается регистр `WHO_AM_I`;
- найденный адрес сохраняется в `s_mpu.addr`.

Если устройство не найдено или не отвечает, функция немедленно возвращает ошибку.

### 3. Пробуждение датчика

Далее в `PWR_MGMT_1` записывается `0x00`:

```c
err = i2c_bus_write(s_mpu.addr, MPU_REG_PWR_MGMT_1, &pwr, 1);
```

Здесь `pwr` равен `0`. Смысл операции — вывести MPU из sleep-состояния.

### 4. Чтение конфигурации гироскопа

Из регистра `GYRO_CONFIG` читается текущая конфигурация диапазона измерения. На основе битов `FS_SEL` вычисляется коэффициент пересчета LSB → dps.

Используется helper-функция:

- `app_mpu_gyro_lsb_per_dps()`.

### 5. Чтение конфигурации акселерометра

Из регистра `ACCEL_CONFIG` читается текущая конфигурация диапазона измерения. По полю `AFS_SEL` вычисляется коэффициент пересчета LSB → g.

Используется helper-функция:

- `app_mpu_accel_lsb_per_g()`.

### 6. Сохранение параметров в runtime-state

После успешного чтения параметров функция обновляет `s_mpu`:

- `s_mpu.gyro_lsb_per_dps`;
- `s_mpu.accel_lsb_per_g`;
- `s_mpu.whoami`;
- `s_mpu.ready = true`.

### 7. Логирование результата

В лог выводится строка вида:

```text
ready: addr=0x.. who=0x.. accel_lsb/g=... gyro_lsb/dps=...
```

Это полезно для быстрой аппаратной верификации через monitor.

## Что функция НЕ делает

Важно понимать границы ответственности:

- она не читает текущие значения ускорения/гироскопа;
- она не публикует телеметрию сама;
- она не форматирует длинную pretty-строку;
- она не обновляет `app_mpu_status_t` измерениями.

Все это делает уже `app_mpu_pretty_log_line()` после успешной инициализации.

## Почему эта функция полезна архитектурно

Она отделяет две разные задачи:

1. выяснить, что за устройство подключено и как его интерпретировать;
2. регулярно читать данные и строить телеметрию.

Такое разделение делает код проще:

- init-ошибки и runtime-ошибки не смешиваются;
- scale-коэффициенты вычисляются один раз;
- последующее чтение данных становится компактнее и быстрее.

## Зависимости функции

`app_mpu_pretty_init()` опирается на:

- `mpu9250_probe_and_read_whoami()`;
- `i2c_bus_write()`;
- `i2c_bus_read()`;
- `app_mpu_gyro_lsb_per_dps()`;
- `app_mpu_accel_lsb_per_g()`.

Таким образом, она стоит ровно между sensor-discovery слоем и уровнем прикладной телеметрии.

## Практический вывод

Если бы этой функции не было, то `app_mpu_pretty_log_line()` пришлось бы при каждом вызове:

- заново искать датчик;
- заново вычислять scale;
- смешивать код инициализации с кодом чтения данных.

С текущей реализацией проект получает аккуратную ленивую инициализацию и более чистую архитектуру MPU-подсистемы.



---

## [038] 04-functions/app_mpu_pretty_log_line.md

# app_mpu_pretty_log_line

Исходник: `components/app/src/app_mpu_pretty.c`.

`app_mpu_pretty_log_line()` — это функция прикладного уровня, которая превращает сырые регистровые данные MPU в удобную для человека и внешних систем телеметрию. Она находится выше низкоуровневого слоя I2C и выше простого WHO_AM_I probe: здесь проект уже получает осмысленные физические величины.

## Зачем она нужна

Если `mpu9250_probe_and_read_whoami()` отвечает на вопрос «датчик вообще найден?», то `app_mpu_pretty_log_line()` отвечает на следующий уровень вопроса: «датчик реально отдает полезные измерения, и можем ли мы их интерпретировать?».

Эта функция особенно важна для демонстрационного и учебного проекта, потому что она делает данные:

- читаемыми человеком;
- пригодными для логов;
- пригодными для машинного анализа через телеметрию;
- связанными со временем работы устройства.

## Что делает функция по шагам

На каждом вызове функция проходит примерно такой конвейер:

1. Вычисляет `uptime` системы.
2. Вызывает `app_mpu_pretty_init()`, если модуль еще не готов.
3. Если инициализация/доступ к датчику не удались, публикует telemetry об ошибке.
4. Читает 14 байт из регистра `MPU_REG_ACCEL_XOUT_H`.
5. Разбирает буфер на accel X/Y/Z, temperature, gyro X/Y/Z.
6. Конвертирует сырые значения accel в $g$.
7. Конвертирует сырые значения gyro в $dps$.
8. Конвертирует сырую температуру в градусы Цельсия.
9. Печатает человекочитаемую строку в лог.
10. Вызывает `app_mpu_emit_telemetry_ready()` для machine-readable представления.

Таким образом одна операция чтения датчика сразу обслуживает и удобство человека, и внешний telemetry pipeline.

## Почему читается именно блок из 14 байт

MPU семейства 6050/6500/9250 хранит ускорения, температуру и гироскопические данные подряд. Это позволяет одним burst-read получить целостный снимок состояния сенсора.

Порядок байтов такой:

- accel X/Y/Z;
- temperature;
- gyro X/Y/Z.

Такой пакетный доступ эффективнее, чем раздельное чтение каждого канала, потому что:

- уменьшает накладные расходы по I2C;
- снижает вероятность чтения несогласованных данных между регистрами;
- лучше подходит для периодической телеметрии.

## Что делает функцию «pretty»

Название здесь не случайно. Функция не ограничивается выдачей raw integers, а выполняет прикладную нормализацию:

- accel переводится в $g$;
- gyro — в градусы в секунду;
- температура — в $^\circ C$.

Благодаря этому логи сразу становятся интерпретируемыми без ручного пересчета коэффициентов и обращения к datasheet на каждом шаге.

## Поведение при ошибке

Если датчик неинициализирован или чтение не удалось, функция не делает вид, что данные валидны. Вместо этого она выдает telemetry о проблеме. Это важно для надежности: внешний наблюдатель видит не «нулевые значения», а корректно зафиксированное состояние ошибки.

## Связь с общей телеметрией системы

`app_mpu_pretty_log_line()` встроена в главный цикл приложения через `app_tick()`. Поэтому данные MPU обновляются синхронно с остальной логикой системы — stepper, network tick и общими статусами.

В итоге одна и та же sensor-подсистема участвует сразу в трех уровнях наблюдаемости:

- локальный лог для разработчика;
- `@telemetry` строки;
- агрегированная JSON-телеметрия через сетевой слой.

## Практический смысл

Для курсовой работы эту функцию можно описывать как прикладной уровень обработки первичных данных инерциального датчика, где низкоуровневый доступ к регистрам преобразуется в инженерно интерпретируемые параметры движения и температуры.

См. также:

- [[04-functions/app_mpu_pretty_init]]
- [[04-functions/app_tick]]
- [[02-architecture/Telemetry architecture]]



---

## [039] 04-functions/app_mpu_whoami_check.md

# app_mpu_whoami_check

Исходник: `components/app/src/app.c`.

`app_mpu_whoami_check()` проверяет, виден ли MPU-сенсор на I2C.

Что делает:

- печатает блок `MPU WHOAMI CHECK`;
- вызывает `mpu9250_probe_and_read_whoami(&addr, &who)`;
- если сенсор найден, логирует адрес, WHO_AM_I и имя модели;
- если сенсор не найден, деинициализирует I2C bus;
- запускает `i2c_bus_diag_sweep_mpu_pairs()` для перебора возможных SDA/SCL пар.

Почему функция деинициализирует I2C перед sweep:

- основной bus уже занял конкретные GPIO;
- диагностический sweep создает временные bus на разных парах GPIO;
- активный bus надо отпустить, чтобы не конфликтовать с диагностикой.

Связи:

- [[04-functions/mpu9250_probe_and_read_whoami]]
- [[04-functions/i2c_bus_deinit]]
- [[04-functions/i2c_bus_diag_sweep_mpu_pairs]]



---

## [040] 04-functions/app_net_build_json.md

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



---

## [041] 04-functions/app_net_command_handler.md

# app_net_command_handler

Исходник: `components/app/src/app_net.c`.

`app_net_command_handler()` обрабатывает `POST /api/command`.

Что делает:

- читает body через `httpd_req_recv()`;
- проверяет, что body не пустой;
- достает команду через `app_net_extract_command()`;
- вызывает `app_stepper_command_char(cmd)`;
- если команда обработана, возвращает обычный telemetry JSON через `app_net_telemetry_handler(req)`.

Пример запроса:

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"s"}'
```

Связи:

- [[04-functions/app_net_extract_command]]
- [[04-functions/app_stepper_command_char]]
- [[04-functions/app_net_telemetry_handler]]



---

## [042] 04-functions/app_net_extract_command.md

# app_net_extract_command

Исходник: `components/app/src/app_net.c`.

`app_net_extract_command()` достает один символ команды из HTTP body или WebSocket payload.

Поддерживаемые формы:

```json
{"command":"f"}
```

или короткая форма:

```text
f
```

Алгоритм:

- если есть `"command"`, ищет `:`, затем первую кавычку после двоеточия;
- берет первый символ после кавычки;
- если `"command"` нет, ищет первый непробельный символ, игнорируя пробелы, CR, LF, tab и кавычку;
- возвращает `true`, если команда найдена.

Ограничение:

- это не полноценный JSON parser;
- для текущих односимвольных команд это достаточно, но при сложном API лучше заменить на JSON parser.



---

## [043] 04-functions/app_net_options_handler.md

# app_net_options_handler

Исходник: `components/app/src/app_net.c`.

`app_net_options_handler()` отвечает на CORS preflight запросы.

Что делает:

- вызывает `app_net_set_cors(req)`;
- отправляет пустой ответ.

Зачем это нужно:

- браузер может отправить `OPTIONS` перед `POST /api/command`;
- без корректных CORS headers веб-приложение на компьютере может получить browser-level блокировку;
- прошивка разрешает `GET`, `POST`, `OPTIONS` и header `Content-Type`.



---

## [044] 04-functions/app_net_queue_ws_send.md

# app_net_queue_ws_send

Исходник: `components/app/src/app_net.c`.

`app_net_queue_ws_send()` ставит асинхронную отправку WebSocket frame в очередь HTTP server.

Что делает:

- проверяет, что server и payload существуют;
- выделяет `app_net_ws_msg_t`;
- сохраняет server handle, socket fd и payload;
- вызывает `httpd_queue_work(s_server, app_net_ws_send_work, msg)`;
- если поставить задачу в очередь не удалось, освобождает память.

Зачем нужна отдельная структура `app_net_ws_msg_t`:

- async work выполнится позже;
- payload должен жить дольше, чем stack frame текущей функции;
- поэтому данные копируются в heap object.



---

## [045] 04-functions/app_net_set_cors.md

# app_net_set_cors

Исходник: `components/app/src/app_net.c`.

`app_net_set_cors()` выставляет CORS headers для HTTP response.

Headers:

- `Access-Control-Allow-Origin: *`;
- `Access-Control-Allow-Methods: GET,POST,OPTIONS`;
- `Access-Control-Allow-Headers: Content-Type`.

Это нужно, чтобы веб-приложение на компьютере могло делать запросы к ESP с другого origin.



---

## [046] 04-functions/app_net_start.md

# app_net_start

Исходник: `components/app/src/app_net.c`.

`app_net_start()` запускает сетевой интерфейс прикладного уровня: HTTP server, REST endpoints и WebSocket endpoint для потоковой телеметрии. Если `app_wifi_smoke_run()` отвечает за появление сетевой среды, то `app_net_start()` отвечает за то, чтобы в этой среде появился реальный API приложения.

## Роль в общей архитектуре

Эта функция связывает embedded-логику проекта с внешним миром. До ее вызова плата может уже быть доступна по Wi‑Fi, но пользователь еще не имеет прикладных точек входа для чтения телеметрии и отправки команд. После успешного `app_net_start()` система становится управляемой по HTTP/WebSocket.

В архитектурной цепочке это выглядит так:

1. `app_init()` инициализирует локальные подсистемы.
2. `app_wifi_smoke_run()` поднимает Wi‑Fi.
3. `app_net_start()` публикует API поверх уже существующей сетевой инфраструктуры.

## Что делает функция по шагам

Базовый сценарий работы:

1. Проверяет, не запущен ли сервер уже сейчас.
2. Если сервер уже существует (`s_server != NULL`), возвращает `ESP_OK` без повторной инициализации.
3. Создает конфигурацию `httpd_config_t` на базе `HTTPD_DEFAULT_CONFIG()`.
4. Подстраивает параметры сервера, в частности увеличивает `max_uri_handlers`.
5. Вызывает `httpd_start(&s_server, &config)`.
6. После успешного старта регистрирует набор URI handlers.

Регистрация маршрутов — это фактическое описание контрактов, которые система предлагает внешним клиентам.

## Какие endpoint'ы поднимаются

После старта сервер обслуживает несколько типов взаимодействия:

- `GET /api/telemetry` — агрегированная JSON-телеметрия устройства;
- `GET /api/wifi` — отдельный снимок состояния Wi‑Fi;
- `POST /api/command` — прием команд управления шаговым двигателем;
- `OPTIONS /*` — CORS/preflight сценарии для браузерных клиентов;
- `GET /ws` — WebSocket endpoint для push-модели телеметрии.

Именно этот набор делает возможным и «ручное» взаимодействие через браузер/скрипт, и более живой UI с периодическими обновлениями через WebSocket.

## Почему запуск вынесен в отдельную функцию

Такое разделение удобно по нескольким причинам:

- Wi‑Fi и API — это разные слои системы;
- можно поднять Wi‑Fi, но не поднимать API при ошибке/отладке;
- можно централизованно документировать и контролировать точку публикации внешнего интерфейса.

Для embedded-проекта это хороший паттерн: сначала поднимается транспорт, потом прикладной протокол.

## Важные условия и ограничения

- `app_net_start()` вызывается из `app_init()` только если базовая сеть готова;
- WebSocket-маршрут имеет смысл только при включенном `CONFIG_HTTPD_WS_SUPPORT=y`;
- если `httpd_start()` возвращает ошибку, система продолжает жить как embedded-устройство, но без сетевого API;
- функция не занимается периодической рассылкой — это уже зона ответственности `app_net_tick()`.

То есть запуск сервера и его регулярное обслуживание сознательно разделены.

## Почему функция идемпотентна

Проверка `s_server != NULL` делает функцию безопасной для повторного вызова. Это важно в прикладной архитектуре: повторный старт не должен создавать второй сервер, дублировать handlers или ломать существующие сокеты.

## Что получает пользователь после успешного вызова

После `app_net_start()` система становится доступной по нескольким режимам взаимодействия:

- можно прочитать текущее состояние устройства в JSON;
- можно увидеть Wi‑Fi статус без UART;
- можно послать команду шаговому двигателю через HTTP;
- можно подписаться на живую телеметрию через WebSocket.

С точки зрения курсовой это важная инженерная точка: устройство из «локально работающего embedded стенда» превращается в сетевой киберфизический узел с удаленным API.

См. также:

- [[04-functions/app_net_tick]]
- [[04-functions/app_net_build_json]]
- [[02-architecture/WiFi HTTP WebSocket architecture]]



---

## [047] 04-functions/app_net_telemetry_handler.md

# app_net_telemetry_handler

Исходник: `components/app/src/app_net.c`.

`app_net_telemetry_handler()` обрабатывает `GET /api/telemetry`.

Что делает:

- выделяет stack buffer `json`;
- вызывает `app_net_build_json()`;
- выставляет CORS headers через `app_net_set_cors()`;
- выставляет response type `application/json`;
- отправляет строку через `httpd_resp_sendstr()`.

Эта функция также используется после успешной команды в `POST /api/command`, чтобы клиент сразу получил новое состояние.



---

## [048] 04-functions/app_net_tick.md

# app_net_tick

Исходник: `components/app/src/app_net.c`.

`app_net_tick()` — это периодический сервисный обработчик сетевой подсистемы. Он не поднимает сервер и не принимает новые HTTP-запросы напрямую; его главная задача — организовать push-рассылку телеметрии активным WebSocket-клиентам.

## Роль в runtime-модели проекта

В проекте используется кооперативная схема с единым циклом `app_tick()`. В этой схеме каждая подсистема получает небольшой регулярный квант времени. `app_net_tick()` — это именно такой квант для сетевого слоя.

Идея простая:

- HTTP server живет сам по себе после `app_net_start()`;
- а вот периодическая отправка актуальной телеметрии инициируется из главного цикла приложения.

Это делает поведение системы предсказуемым: частота push-обновлений контролируется приложением, а не случайным набором фоновых таймеров.

## Что делает функция

Типовой проход `app_net_tick()` выглядит так:

1. Проверяет, запущен ли сервер.
2. Если сервера нет, сразу выходит.
3. Проверяет, прошло ли достаточно времени с предыдущей рассылки.
4. Получает список подключенных клиентов через `httpd_get_client_list()`.
5. Строит единый JSON снимок через `app_net_build_json()`.
6. Для каждого дескриптора проверяет, относится ли он к WebSocket-соединению.
7. Для WebSocket-клиентов ставит отправку в очередь через `app_net_queue_ws_send()`.

Таким образом одна и та же телеметрия рассылается всем актуальным подписчикам без повторной сборки JSON для каждого клиента.

## Почему здесь используется периодический интервал

Рассылка выполняется не на каждом вызове `app_tick()`, а примерно раз в секунду. Это разумный компромисс между:

- свежестью данных;
- объемом трафика;
- нагрузкой на CPU;
- шумом в браузерном/внешнем клиенте.

Для лабораторного проекта такой ритм обычно достаточен: пользователь видит живое состояние, но система не превращается в генератор лишних пакетов.

## Почему отправка идет через очередь работы HTTP server

Важная деталь реализации — фактическая отправка делегируется через `httpd_queue_work`. Это соответствует ожиданиям ESP-IDF HTTP server и защищает от проблем, которые часто возникают при попытке отправить WebSocket frame из «чужого» контекста.

Иначе говоря, `app_net_tick()` не ломает модель владения сервером, а аккуратно просит сервер выполнить отправку в своем корректном execution context.

Это снижает риск:

- гонок по socket state;
- некорректной работы из неподходящего потока выполнения;
- трудноуловимых сетевых ошибок на больших сериях обновлений.

## Что особенно важно для архитектуры

`app_net_tick()` показывает, что в проекте push-телеметрия сделана без отдельной RTOS task специально под WebSocket. Вместо этого используется общий цикл приложения и внутренняя очередь сервера. Это упрощает архитектуру и снижает число независимо живущих контекстов.

Для небольшого embedded-приложения это сильное инженерное решение: меньше конкурирующих задач — проще анализ и отладка.

## Связь с другими функциями

- `app_net_start()` поднимает сервер и маршруты;
- `app_net_build_json()` формирует полезную нагрузку;
- `app_tick()` регулярно вызывает `app_net_tick()`;
- WebSocket handler обеспечивает подключение клиента, а `app_net_tick()` — дальнейшую потоковую доставку данных.

## Что функция не делает

`app_net_tick()` не:

- стартует Wi‑Fi;
- открывает новые endpoints;
- парсит HTTP POST-команды;
- управляет stepper напрямую;
- читает датчики самостоятельно.

Она работает как сетевой «диспетчер рассылки», используя уже подготовленные данные других подсистем.

См. также:

- [[04-functions/app_net_start]]
- [[04-functions/app_net_build_json]]
- [[04-functions/app_tick]]



---

## [049] 04-functions/app_net_wifi_handler.md

# app_net_wifi_handler

Исходник: `components/app/src/app_net.c`.

`app_net_wifi_handler()` обрабатывает `GET /api/wifi`.

Что делает:

- получает `app_wifi_status_t` через `app_wifi_get_status()`;
- вручную собирает JSON только про Wi-Fi;
- если `snprintf` вернул ошибку, отправляет `HTTPD_500_INTERNAL_SERVER_ERROR`;
- выставляет CORS headers;
- выставляет `application/json`;
- отправляет JSON.

Используется для проверки сети без чтения stepper telemetry.



---

## [050] 04-functions/app_net_ws_handler.md

# app_net_ws_handler

Исходник: `components/app/src/app_net.c`.

`app_net_ws_handler()` обслуживает WebSocket endpoint `/ws`.

Поведение при `HTTP_GET`:

- это handshake;
- логирует подключение;
- возвращает `ESP_OK`.

Поведение при WebSocket frame:

- сначала вызывает `httpd_ws_recv_frame(req, &frame, 0)`, чтобы узнать длину;
- выделяет payload буфер через `calloc`;
- читает frame целиком;
- если frame текстовый и непустой, пытается достать команду;
- если команда найдена, вызывает `app_stepper_command_char(cmd)`;
- освобождает payload;
- строит свежий JSON;
- отправляет JSON как WebSocket text frame.

Отдельно `app_net_tick()` позже рассылает heartbeat telemetry всем WebSocket-клиентам.



---

## [051] 04-functions/app_net_ws_send_work.md

# app_net_ws_send_work

Исходник: `components/app/src/app_net.c`.

`app_net_ws_send_work()` выполняет фактическую асинхронную отправку WebSocket frame.

Что делает:

- получает `app_net_ws_msg_t *`;
- создает `httpd_ws_frame_t`;
- выставляет `final = true`;
- выставляет `type = HTTPD_WS_TYPE_TEXT`;
- отправляет frame через `httpd_ws_send_frame_async()`;
- при ошибке пишет warning;
- освобождает `msg`.

Функция вызывается не напрямую из app loop, а через `httpd_queue_work()`.



---

## [052] 04-functions/app_stepper_apply_named_phase.md

# app_stepper_apply_named_phase

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_apply_named_phase()` удерживает конкретную фазу `A`, `B`, `C` или `D`.

Что делает:

- проверяет, что индекс фазы допустим;
- переводит stepper в режим `stop`;
- записывает `phase_index`;
- применяет выбранную фазу;
- логирует уровни IN1..IN4;
- печатает telemetry `hold_phase`.

Используется командами:

- `a`
- `b`
- `c`
- `d`



---

## [053] 04-functions/app_stepper_apply_phase.md

# app_stepper_apply_phase

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_apply_phase()` применяет одну фазу к GPIO входам L293D.

Что делает:

- выставляет IN1;
- выставляет IN2;
- выставляет IN3;
- выставляет IN4;
- ставит `s_stepper.coils_enabled = true`;
- переключает activity LED через `app_stepper_led_toggle()`.

Фаза передается как `app_stepper_phase_t`, где есть четыре логических уровня и label.



---

## [054] 04-functions/app_stepper_cmd_to_str.md

# app_stepper_cmd_to_str

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_cmd_to_str()` переводит последний command byte в строку.

Особые случаи:

- `0` -> пустая строка;
- `'\r'` -> `\\r`;
- `'\n'` -> `\\n`;
- иначе возвращается однобуквенная строка.

Функция использует static buffer на 2 символа для обычных команд.



---

## [055] 04-functions/app_stepper_command_char.md

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



---

## [056] 04-functions/app_stepper_delay_adjust_delta_ms.md

# app_stepper_delay_adjust_delta_ms

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_delay_adjust_delta_ms()` выбирает размер изменения задержки шага.

Логика:

- при delay >= 1000 мс шаг регулировки 200 мс;
- при delay >= 500 мс шаг регулировки 100 мс;
- при delay >= 250 мс шаг регулировки 50 мс;
- при delay >= 100 мс шаг регулировки 20 мс;
- иначе 10 мс.

Зачем это нужно:

- на медленных скоростях грубое изменение удобно;
- на быстрых скоростях изменение должно быть точнее;
- команды `+` и `-` ощущаются более управляемо.



---

## [057] 04-functions/app_stepper_emit_telemetry.md

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



---

## [058] 04-functions/app_stepper_get_snapshot.md

# app_stepper_get_snapshot

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_get_snapshot()` копирует внутреннее состояние stepper в публичную структуру `app_stepper_snapshot_t`.

Что копируется:

- mode;
- sweep_state;
- step_delay_ms;
- steps_per_second;
- phase_index;
- total_steps;
- sweep_steps;
- coils_enabled;
- uart_ready;
- last_command;
- GPIO для IN1..IN4;
- LED GPIO или `-1`, если LED выключен.

Зачем это нужно:

- `app_net.c` может строить JSON без знания внутренних enum и state struct;
- публичный API остается узким;
- можно менять внутреннее устройство stepper, не переписывая сетевой слой.



---

## [059] 04-functions/app_stepper_gpio_init.md

# app_stepper_gpio_init

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_gpio_init()` настраивает четыре GPIO, подключенные к входам L293D.

Пины берутся из Kconfig:

- `CONFIG_APP_L293D_IN1_GPIO`
- `CONFIG_APP_L293D_IN2_GPIO`
- `CONFIG_APP_L293D_IN3_GPIO`
- `CONFIG_APP_L293D_IN4_GPIO`

Настройка:

- mode: `GPIO_MODE_OUTPUT`;
- pull-up: disabled;
- pull-down: disabled;
- interrupt: disabled.

Функция возвращает результат `gpio_config(&cfg)`.



---

## [060] 04-functions/app_stepper_handle_command.md

# app_stepper_handle_command

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_handle_command()` — центральная точка интерпретации команд управления шаговым двигателем. Именно здесь символьный ввод превращается в конкретные изменения режима, направления, скорости, состояния удержания фаз и диагностического поведения модуля.

## Почему эта функция архитектурно важна

Одна из сильных сторон проекта — единый командный путь для разных транспортов управления. Команда может прийти:

- из UART;
- из HTTP/JSON API;
- потенциально из WebSocket/UI.

Но в итоге она должна быть интерпретирована одинаково. `app_stepper_handle_command()` обеспечивает именно это: независимо от происхождения символа семантика команды одинакова.

Это резко упрощает систему:

- не нужно поддерживать две разные логики управления;
- поведение UART и network-контроля остается согласованным;
- документация команд пишется один раз.

## Какие команды поддерживаются

Функция обрабатывает компактный символьный протокол:

- `h` — вывести help;
- `p` — показать текущее состояние;
- `s` — остановить движение;
- `f` — включить вращение вперед;
- `r` — включить вращение назад;
- `w` — перейти в sweep-режим;
- `1` — выполнить один шаг вперед;
- `2` — выполнить один шаг назад;
- `a`, `b`, `c`, `d` — удерживать конкретную фазу;
- `+`, `=` — ускорить двигатель за счет уменьшения delay;
- `-`, `_` — замедлить двигатель за счет увеличения delay;
- `z` — отпустить обмотки.

По сути это человеко-читаемый минималистичный протокол управления исполнительным механизмом.

## Что меняет функция внутри подсистемы

В зависимости от команды функция может:

- переключить режим state machine;
- изменить направление вращения;
- выполнить единичный шаг;
- скорректировать временные параметры;
- изменить состояние обмоток;
- инициировать вывод диагностической информации.

Важно, что логика изменения состояния сконцентрирована здесь, а не размазана по UART handler, HTTP handler и tick-циклу.

## Защита от дублей

В коде предусмотрен guard: повтор той же команды в пределах `APP_STEPPER_DUPLICATE_CMD_GUARD_MS` игнорируется.

Это небольшая, но очень полезная деталь. В реальной системе дубли могут появляться из-за:

- дребезга терминального ввода;
- повторной отправки команды UI;
- слишком частых пользовательских кликов;
- особенностей транспортного уровня.

Без защиты двигатель мог бы получать лишние переходы состояния, особенно при переключении режимов или изменении скорости. Guard делает поведение системы стабильнее и предсказуемее.

## Почему выбран символьный протокол

Для учебного, лабораторного и отладочного проекта такой подход удобен:

- команда легко набирается руками в UART monitor;
- ее просто отправить через HTTP API;
- команды легко логировать и документировать;
- их семантика достаточно прозрачна для демонстрации.

Это не промышленный бинарный протокол, а сознательно упрощенный интерфейс управления, оптимальный для разработки, обучения и быстрых экспериментов.

## Связь с другими функциями

Фактический поток обычно выглядит так:

1. Символ приходит из UART или HTTP.
2. Транспортный слой передает его в stepper-модуль.
3. `app_stepper_handle_command()` меняет внутреннее состояние.
4. `app_stepper_tick()` реализует это состояние во времени.
5. `app_stepper_get_snapshot()` отдает актуальный статус наружу.

Это классический split между command plane и execution plane.

## Практический смысл

Если в пояснительной записке нужно описать унификацию локального и удаленного управления, именно `app_stepper_handle_command()` является ключевым аргументом: в проекте один и тот же исполнительный механизм управляется через единое командное ядро, а различаются только каналы доставки команды.

См. также:

- [[04-functions/app_stepper_init]]
- [[04-functions/app_stepper_tick]]
- [[02-architecture/UART and network dual control]]



---

## [061] 04-functions/app_stepper_handle_uart.md

# app_stepper_handle_uart

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_handle_uart()` читает входящие байты из UART0.

Что делает:

- создает буфер `uint8_t buf[16]`;
- вызывает `uart_read_bytes(APP_STEPPER_UART_PORT, buf, sizeof(buf), 0)`;
- если байтов нет, выходит;
- для каждого прочитанного байта вызывает `app_stepper_handle_command(buf[i])`.

Таймаут чтения равен `0`, поэтому функция не блокирует главный цикл.



---

## [062] 04-functions/app_stepper_init.md

# app_stepper_init

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_init()` подготавливает к работе всю подсистему управления шаговым двигателем через драйвер L293D. Эта функция не просто настраивает GPIO — она формирует начальное операционное состояние модуля: аппаратные линии, индикацию, UART-канал команд, стартовый режим и первичную телеметрию.

## Зачем эта функция нужна

В архитектуре проекта stepper-модуль должен уметь работать сразу по нескольким каналам управления:

- локально через UART;
- удаленно через HTTP/WebSocket API;
- автономно в sweep-режиме внутри `app_stepper_tick()`.

Чтобы это было возможно, модуль должен стартовать в согласованном состоянии. Именно это и делает `app_stepper_init()`.

## Что происходит при инициализации

Функция выполняет последовательность шагов, которая важна не только технически, но и логически:

1. Печатает стартовый диагностический блок `L293D STEPPER UART CONTROL`.
2. Настраивает выходные GPIO для управления фазами двигателя.
3. При необходимости настраивает LED-индикацию.
4. Вызывает `app_stepper_release()`, чтобы не оставлять катушки в неопределенном или удерживающем состоянии на старте.
5. Инициализирует UART-интерфейс приема команд.
6. Печатает параметры конфигурации: GPIO, задержку шага, UART settings.
7. Выводит help по доступным командам.
8. Инициализирует внутренний автомат sweep-режима.
9. Переводит модуль в стартовый режим `APP_STEPPER_MODE_SWEEP`.
10. Публикует стартовую телеметрию `init`.

Такой сценарий позволяет после загрузки получить устройство, которое уже готово к демонстрации поведения даже без внешнего управляющего клиента.

## Почему модуль стартует именно в sweep-режиме

Для лабораторного и демонстрационного стенда sweep — удобный режим по умолчанию:

- двигатель начинает проявлять «живое» поведение без сложной подготовки;
- можно быстро проверить правильность фаз, проводки и реакции механики;
- удобно видеть, что `app_tick()` и stepper state machine действительно работают.

Если бы старт происходил сразу в idle, пользователь мог бы ошибочно решить, что система неинициализирована или мотор не отвечает.

## Почему ошибка UART не считается фатальной

Это одна из самых важных инженерных деталей функции. Если `app_stepper_uart_init()` неудачен, код логирует warning, но не отключает саму моторную логику.

Причина практическая: UART — только один из каналов управления. Даже при его отказе остаются:

- логика вращения;
- локальный state machine;
- сетевой путь через HTTP/WebSocket.

Такой подход повышает отказоустойчивость демонстрационного стенда: частичная потеря интерфейса управления не превращается в полный отказ функциональности.

## Что подготавливается внутри модуля

После успешного выполнения `app_stepper_init()` подсистема имеет:

- настроенные линии фаз двигателя;
- определенное начальное состояние обмоток;
- выбранный режим работы;
- стартовое направление sweep-автомата;
- готовность принимать команды символами;
- начальную телеметрию для логов и внешнего наблюдения.

## Как это связано с дальнейшей работой

После `app_stepper_init()` основной runtime идет через:

- `app_stepper_tick()` — периодическое выполнение движения и обработка автомата;
- `app_stepper_command_char()` / `app_stepper_handle_command()` — реакция на команды пользователя;
- `app_stepper_get_snapshot()` — выдача состояния наружу для JSON/API.

То есть `app_stepper_init()` — это не единичное действие, а входная точка во весь жизненный цикл stepper-подсистемы.

## Практический вывод

Если описывать модуль в курсовой, `app_stepper_init()` — это процедура перевода драйвера шагового двигателя из пассивного набора GPIO и параметров в наблюдаемую и управляемую подсистему с несколькими каналами управления и безопасным стартовым состоянием.

См. также:

- [[04-functions/app_stepper_tick]]
- [[04-functions/app_stepper_handle_command]]
- [[03-components/app_stepper]]



---

## [063] 04-functions/app_stepper_led_init.md

# app_stepper_led_init

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_led_init()` компилирует полезное тело только если включен `CONFIG_APP_STEPPER_LED_ENABLE`.

Что делает при включенном LED:

- настраивает `CONFIG_APP_STEPPER_LED_GPIO` как output;
- выставляет уровень `0`.

Если LED выключен в конфиге, функция фактически пустая.



---

## [064] 04-functions/app_stepper_led_set.md

# app_stepper_led_set

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_led_set()` выставляет activity LED в конкретное состояние.

Если `CONFIG_APP_STEPPER_LED_ENABLE` включен:

- `on == true` -> GPIO level `1`;
- `on == false` -> GPIO level `0`.

Если LED выключен в конфиге, аргумент гасится через `(void)on`.



---

## [065] 04-functions/app_stepper_led_toggle.md

# app_stepper_led_toggle

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_led_toggle()` переключает activity LED.

Что делает при включенном `CONFIG_APP_STEPPER_LED_ENABLE`:

- инвертирует `s_stepper.led_state`;
- пишет новый уровень в `CONFIG_APP_STEPPER_LED_GPIO`.

Вызывается при применении фазы, то есть LED может мигать на шагах двигателя.



---

## [066] 04-functions/app_stepper_log_block.md

# app_stepper_log_block

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_log_block()` печатает цветной блок-разделитель для stepper логов.

Используется в `app_stepper_init()` перед выводом информации о L293D/UART управлении.

Функция не меняет состояние мотора.



---

## [067] 04-functions/app_stepper_log_timing.md

# app_stepper_log_timing

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_log_timing()` печатает текущую задержку шага и скорость в шагах в секунду.

Используется после команд:

- `+`;
- `=`;
- `-`;
- `_`.

После лога вызывает `app_stepper_emit_telemetry(reason)`.



---

## [068] 04-functions/app_stepper_mode_to_str.md

# app_stepper_mode_to_str

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_mode_to_str()` переводит enum режима stepper в строку.

Значения:

- `APP_STEPPER_MODE_STOP` -> `stop`;
- `APP_STEPPER_MODE_FORWARD` -> `forward`;
- `APP_STEPPER_MODE_REVERSE` -> `reverse`;
- `APP_STEPPER_MODE_SWEEP` -> `sweep`;
- default -> `unknown`.

Используется в логах, UART telemetry и HTTP/WebSocket snapshot.



---

## [069] 04-functions/app_stepper_print_help.md

# app_stepper_print_help

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_print_help()` печатает список команд stepper.

Команды включают:

- help/status;
- stop/forward/reverse/sweep;
- single-step forward/reverse;
- hold phase A/B/C/D;
- speed up / slow down;
- release coils.

Это справка для UART пользователя, но команды совпадают с network API.



---

## [070] 04-functions/app_stepper_print_status.md

# app_stepper_print_status

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_print_status()` печатает состояние stepper.

Поля:

- mode;
- delay;
- steps/s;
- phase;
- total_steps;
- coils;
- sweep_steps;
- uart state.

После text log вызывает `app_stepper_emit_telemetry("status")`.



---

## [071] 04-functions/app_stepper_release.md

# app_stepper_release

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_release()` отпускает обмотки двигателя.

Что делает:

- выставляет все IN1..IN4 в `0`;
- ставит `s_stepper.coils_enabled = false`;
- сбрасывает `s_stepper.led_state = false`;
- выключает LED через `app_stepper_led_set(false)`.

Это важно для:

- режима `stop`;
- пауз sweep на краях;
- команды `z`;
- безопасного начального состояния после init.



---

## [072] 04-functions/app_stepper_set_mode.md

# app_stepper_set_mode

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_set_mode()` меняет режим движения.

Режимы:

- `APP_STEPPER_MODE_STOP`
- `APP_STEPPER_MODE_FORWARD`
- `APP_STEPPER_MODE_REVERSE`
- `APP_STEPPER_MODE_SWEEP`

Что делает:

- если режим уже такой же, ничего не меняет;
- обновляет `s_stepper.mode`;
- сбрасывает pause/tick счетчики;
- если новый режим `stop`, вызывает `app_stepper_release()`;
- если режим не `stop`, сбрасывает `last_step_ms`, чтобы следующий tick мог шагнуть сразу;
- печатает telemetry.



---

## [073] 04-functions/app_stepper_step_forward_once.md

# app_stepper_step_forward_once

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_step_forward_once()` делает один шаг вперед.

Алгоритм:

- считает количество фаз;
- применяет текущую фазу `s_phases[s_stepper.phase_index]`;
- увеличивает `phase_index`;
- если индекс дошел до конца, возвращает его в `0`;
- увеличивает `total_steps`.

Движение получается за счет последовательного прохода по фазам вперед.



---

## [074] 04-functions/app_stepper_step_reverse_once.md

# app_stepper_step_reverse_once

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_step_reverse_once()` делает один шаг назад.

Алгоритм:

- считает количество фаз;
- если `phase_index == 0`, переносит индекс на последнюю фазу;
- иначе уменьшает `phase_index`;
- применяет фазу;
- увеличивает `total_steps`.

Движение назад получается за счет прохода по той же таблице фаз в обратном направлении.



---

## [075] 04-functions/app_stepper_steps_per_second.md

# app_stepper_steps_per_second

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_steps_per_second()` переводит задержку шага в шаги в секунду.

Формула:

```c
1000.0f / (float)delay_ms
```

Если `delay_ms == 0`, возвращает `0.0f`, чтобы не делить на ноль.

Используется в status и telemetry.



---

## [076] 04-functions/app_stepper_sweep_state_to_str.md

# app_stepper_sweep_state_to_str

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_sweep_state_to_str()` переводит состояние sweep state machine в строку.

Значения:

- `APP_STEPPER_SWEEP_FORWARD` -> `forward`;
- `APP_STEPPER_SWEEP_REVERSE` -> `reverse`;
- `APP_STEPPER_SWEEP_PAUSE_AFTER_FORWARD` -> `pause_after_forward`;
- `APP_STEPPER_SWEEP_PAUSE_AFTER_REVERSE` -> `pause_after_reverse`;
- default -> `unknown`.

Используется в telemetry и snapshot.



---

## [077] 04-functions/app_stepper_tick.md

# app_stepper_tick

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_tick()` выполняет периодическую работу stepper.

## Роль в архитектуре

Это главный runtime-движок моторной подсистемы. Именно здесь внутреннее состояние stepper превращается в реальные шаги, паузы, heartbeat-telemetry и обработку UART-команд.

Что делает:

- читает текущее время через `esp_log_timestamp()`;
- если UART готов, вызывает `app_stepper_handle_uart()`;
- раз в секунду печатает heartbeat telemetry;
- если режим `stop`, выходит;
- если режим `sweep`, управляет автоматическим движением вперед/назад и паузами;
- если режим `forward`, делает шаг вперед с учетом задержки;
- если режим `reverse`, делает шаг назад с учетом задержки.

Timing logic:

- каждый шаг разрешен только если прошло `s_stepper.step_delay_ms`;
- для sweep после `APP_STEPPER_SWEEP_STEPS` шагов включается пауза;
- пауза длится `APP_STEPPER_EDGE_PAUSE_MS`.

## Как устроен режим `sweep`

Логика sweep делится на несколько состояний:

- движение вперед;
- пауза после forward;
- движение назад;
- пауза после reverse.

Внутри функции это реализовано как state machine через `s_stepper.sweep_state`. Такой подход удобен тем, что двигатель не блокирует главный цикл ожиданиями — все строится через сравнение timestamp'ов.

## Дополнительная телеметрия

Раз в секунду функция генерирует heartbeat через `app_stepper_emit_telemetry("heartbeat")`.

Это полезно не только для UART/log, но и косвенно для общей наблюдаемости системы: даже без активных команд видно, что моторный runtime жив и обслуживается.

## Почему функция важна

На примере `app_stepper_tick()` особенно хорошо видно, как в проекте реализован неблокирующий embedded-loop:

- время сравнивается через timestamp;
- шаги делаются только при наступлении нужного интервала;
- переходы режима не требуют отдельного потока;
- одна функция обслуживает и UART, и движение, и heartbeat.

Связи:

- [[04-functions/app_stepper_handle_uart]]
- [[04-functions/app_stepper_step_forward_once]]
- [[04-functions/app_stepper_step_reverse_once]]
- [[04-functions/app_stepper_release]]



---

## [078] 04-functions/app_stepper_uart_init.md

# app_stepper_uart_init

Исходник: `components/app/src/app_stepper.c`.

`app_stepper_uart_init()` поднимает старый UART control path.

Что делает:

- настраивает `UART_NUM_0`;
- ставит baud rate из `CONFIG_APP_STEPPER_UART_BAUD_RATE`;
- использует 8 data bits;
- отключает parity;
- использует 1 stop bit;
- отключает hardware flow control;
- устанавливает UART driver через `uart_driver_install()`;
- применяет параметры через `uart_param_config()`;
- ставит режим `UART_MODE_UART`;
- выставляет `s_stepper.uart_ready = true`.

Если `uart_driver_install()` возвращает `ESP_ERR_INVALID_STATE`, это не считается фатальной ошибкой: драйвер уже мог быть установлен.



---

## [079] 04-functions/app_tick.md

# app_tick

Исходник: `components/app/src/app.c`.

`app_tick()` - периодическая функция приложения. Ее вызывает `app_main()` каждые `APP_MAIN_TICK_MS` миллисекунд.

## Роль в архитектуре

`app_tick()` — это центральный runtime-диспетчер прикладного слоя. Он не выполняет всю тяжелую работу сам, а координирует периодическую активность других подсистем.

Что делает:

- если включен L293D test mode, вызывает `app_stepper_tick()`;
- если включен network API, вызывает `app_net_tick()`;
- если включен `CONFIG_APP_TICK_LOG`, раз в секунду печатает system telemetry и MPU telemetry.

Почему функция устроена через `#if`:

- ESP-IDF config генерирует compile-time macros;
- ненужный код может быть исключен при сборке;
- один проект можно собирать в разных режимах.

## Что происходит при включенном `CONFIG_APP_TICK_LOG`

В этом режиме функция дополнительно:

- отслеживает время через `esp_log_timestamp()`;
- раз в `APP_MPU_LOG_PERIOD_MS` генерирует системную телеметрию;
- вызывает `app_mpu_pretty_log_line()`;
- при ошибке MPU сохраняет `last_error` в системном статусе.

Это означает, что `app_tick()` является не только scheduler-подобной функцией, но и точкой синхронизации периодической телеметрии проекта.

## Почему функция важна

Через нее видно главный стиль всей прошивки:

- нет тяжелого блокирующего цикла на одну подсистему;
- есть один короткий общий loop;
- все периодические действия разложены по модулям.

Для курсовой это хороший пример кооперативной модели выполнения в embedded-проекте.

Связи:

- [[04-functions/app_stepper_tick]]
- [[04-functions/app_net_tick]]
- [[04-functions/app_mpu_pretty_log_line]]



---

## [080] 04-functions/app_tick_delay_ms.md

# app_tick_delay_ms

Исходник: `components/app/src/app.c`.

`app_tick_delay_ms()` возвращает задержку главного цикла приложения.

Сейчас значение фиксировано через:

```c
#define APP_MAIN_TICK_MS 5U
```

Фактически это значит, что `app_tick()` вызывается примерно каждые 5 мс.

Важно понимать:

- это не точный real-time таймер;
- FreeRTOS scheduler и другие задачи могут влиять на фактическое время;
- для этой прошивки такой подход достаточен, потому что stepper timing проверяется по `esp_log_timestamp()`.



---

## [081] 04-functions/app_wifi_auth_to_str.md

# app_wifi_auth_to_str

Исходник: `components/app/src/app_wifi.c`.

`app_wifi_auth_to_str()` переводит `wifi_auth_mode_t` в короткую строку.

Примеры:

- `WIFI_AUTH_OPEN` -> `OPEN`;
- `WIFI_AUTH_WPA2_PSK` -> `WPA2-PSK`;
- `WIFI_AUTH_WPA3_PSK` -> `WPA3-PSK`;
- неизвестное значение -> `UNKNOWN`.

Используется при печати результатов Wi-Fi scan.



---

## [082] 04-functions/app_wifi_build_ap_ssid.md

# app_wifi_build_ap_ssid

Исходник: `components/app/src/app_wifi.c`.

`app_wifi_build_ap_ssid()` собирает имя точки доступа ESP.

Формат:

```text
CONFIG_APP_WIFI_AP_SSID_PREFIX-<MAC bytes 3..5>
```

Пример:

```text
JC-ESP32P4M3-A1B2C3
```

Почему добавляется MAC-суффикс:

- если рядом несколько плат, SSID не будут полностью одинаковыми;
- пользователь может отличить свою плату;
- префикс остается читаемым.

Если MAC не передан, функция просто копирует `CONFIG_APP_WIFI_AP_SSID_PREFIX`.



---

## [083] 04-functions/app_wifi_event_handler.md

# app_wifi_event_handler

Исходник: `components/app/src/app_wifi.c`.

`app_wifi_event_handler()` компилируется только если включен `CONFIG_APP_WIFI_CONNECT`.

Назначение:

- обработать STA start;
- вызвать `esp_wifi_connect()`;
- обработать STA disconnect;
- сделать retry до `APP_WIFI_MAX_RETRIES`;
- обработать `IP_EVENT_STA_GOT_IP`;
- записать `sta_connected` и `sta_ip`.

Если `CONFIG_APP_WIFI_SSID` пустой, функция не пытается подключаться.

Сейчас `CONFIG_APP_WIFI_CONNECT` выключен, поэтому этот код не участвует в текущей сборке.



---

## [084] 04-functions/app_wifi_event_handler_common.md

# app_wifi_event_handler_common

Исходник: `components/app/src/app_wifi.c`.

`app_wifi_event_handler_common()` принимает Wi-Fi и IP события от ESP-IDF.

Обрабатываемые события:

- `WIFI_EVENT_AP_START`: выставляет `s_status.ap_started = true`, обновляет IP status.
- `WIFI_EVENT_AP_STOP`: выставляет `s_status.ap_started = false`.
- `IP_EVENT_AP_STAIPASSIGNED`: обновляет IP status, когда клиенту AP выдан IP.

Если включен `CONFIG_APP_WIFI_CONNECT`, функция передает события в `app_wifi_event_handler()`, который занимается STA connect/retry/GOT_IP.

Зачем это нужно:

- Wi-Fi события приходят асинхронно;
- статус нельзя полностью узнать только в момент `esp_wifi_start()`;
- HTTP `/api/wifi` должен видеть обновленную картину.



---

## [085] 04-functions/app_wifi_get_status.md

# app_wifi_get_status

Исходник: `components/app/src/app_wifi.c`.

`app_wifi_get_status()` — это функция чтения текущего сетевого состояния приложения. Она не поднимает Wi‑Fi, не инициирует подключение и не выполняет активные действия. Ее задача — безопасно собрать актуальный снимок состояния подсистемы Wi‑Fi и отдать его внешним потребителям в виде `app_wifi_status_t`.

## Зачем функция нужна в архитектуре

В проекте сетевой слой отделен от слоя управления Wi‑Fi. `app_net.c` не должен напрямую читать внутренние статические переменные из `app_wifi.c`, иначе компоненты стали бы жестко связаны. Поэтому `app_wifi_get_status()` играет роль boundary API: она превращает внутреннее состояние модуля Wi‑Fi в формализованный status object, который можно сериализовать в JSON, показать в REST API и отправить через WebSocket.

Именно благодаря этой функции UI и HTTP API получают не «кусок внутренностей», а стабильную модель состояния.

## Какие данные возвращает

Структура `app_wifi_status_t` описывает текущее состояние сетевой подсистемы:

- `initialized` — Wi‑Fi стек успешно инициализирован;
- `ap_started` — локальная точка доступа действительно поднята;
- `sta_attempted` — был ли вообще запущен сценарий подключения к внешнему роутеру;
- `sta_connected` — удалось ли получить реальное STA-соединение;
- `ap_ssid` — SSID SoftAP, который поднимает плата;
- `ap_ip` — IP адрес AP-интерфейса, через который обычно подключается пользователь;
- `sta_ip` — IP адрес STA-интерфейса, если режим STA включен и соединение получено;
- `last_error` — код/состояние последней ошибки при работе Wi‑Fi.

С практической точки зрения это и есть минимальный набор, достаточный для удаленной диагностики: можно понять, поднялась ли точка доступа, пыталась ли система выйти во внешнюю сеть и получила ли IP.

## Как функция работает

Логика у функции простая, но важная:

1. Берется текущее сохраненное состояние `s_status`.
2. Выполняется `app_wifi_refresh_status_locked()`, чтобы подтянуть максимально свежие поля из реального состояния стеков/netif.
3. В выходную структуру копируются уже обновленные значения.

То есть функция не ограничивается возвратом «старого кеша», а старается перед отдачей сделать статус максимально актуальным.

## Почему это лучше, чем прямой доступ к глобальным переменным

Если бы `app_net.c` напрямую читал внутренние поля Wi‑Fi-модуля, возникли бы типичные проблемы embedded-проекта:

- размытые границы между компонентами;
- сложность изменения внутренней структуры `app_wifi.c` без каскадных правок;
- риск получения несогласованных данных;
- плохая тестируемость и неудобная документируемость.

`app_wifi_get_status()` решает это аккуратно: у подсистемы есть единая «точка правды» для внешнего чтения состояния.

## Кто вызывает

Основные потребители функции:

- `app_net_build_json()` — включает Wi‑Fi блок в общий JSON телеметрии;
- `app_net_wifi_handler()` — отдает отдельный HTTP-ответ по состоянию Wi‑Fi.

Таким образом, один и тот же источник состояния используется и для агрегированной телеметрии, и для специализированного сетевого эндпоинта.

## Что функция принципиально не делает

Важно не перепутать ее с управляющей логикой. `app_wifi_get_status()`:

- не выполняет `esp_wifi_start()`;
- не делает scan автоматически;
- не инициирует reconnect;
- не поднимает HTTP server;
- не меняет режим AP/APSTA.

Это read-only API. Для архитектуры проекта это полезно: функции получения статуса отделены от функций изменения состояния.

## Практический смысл для документации и курсовой

Если описывать систему в терминах архитектуры, `app_wifi_get_status()` — это адаптер между драйверно-событийной моделью Wi‑Fi и внешним диагностическим интерфейсом системы. Она делает сетевую подсистему наблюдаемой, не смешивая наблюдение и управление.

См. также:

- [[04-functions/app_wifi_smoke_run]]
- [[04-functions/app_net_build_json]]
- [[02-architecture/WiFi HTTP WebSocket architecture]]



---

## [086] 04-functions/app_wifi_log_block.md

# app_wifi_log_block

Исходник: `components/app/src/app_wifi.c`.

`app_wifi_log_block()` печатает цветной заголовок в Wi-Fi логах.

Используется перед:

- Wi-Fi bringup;
- Wi-Fi scan results.

Функция purely cosmetic: она не меняет состояние Wi-Fi.



---

## [087] 04-functions/app_wifi_log_scan_results.md

# app_wifi_log_scan_results

Исходник: `components/app/src/app_wifi.c`.

`app_wifi_log_scan_results()` выполняет Wi-Fi scan и печатает найденные точки доступа.

Что делает:

- выделяет массив `wifi_ap_record_t` через `calloc`;
- запускает scan через `esp_wifi_scan_start(&scan_cfg, true)`;
- забирает результаты через `esp_wifi_scan_get_ap_records()`;
- печатает количество найденных AP;
- для каждой AP печатает SSID, RSSI, channel и тип auth;
- освобождает память через `free(records)`.

Зачем функция нужна:

- проверить, что Wi-Fi radio реально видит эфир;
- диагностировать антенну, канал, страну, питание;
- увидеть, находится ли рядом нужная сеть для STA mode.

Риск:

- scan блокирующий, потому что второй аргумент `esp_wifi_scan_start` равен `true`;
- это нормально на boot, но не стоит часто делать в runtime loop.



---

## [088] 04-functions/app_wifi_nvs_init_once.md

# app_wifi_nvs_init_once

Исходник: `components/app/src/app_wifi.c`.

`app_wifi_nvs_init_once()` инициализирует NVS flash.

Зачем Wi-Fi нужен NVS:

- ESP Wi-Fi stack может хранить служебные настройки;
- NVS используется многими ESP-IDF компонентами;
- без NVS часть Wi-Fi функциональности может не стартовать.

Поведение:

- вызывает `nvs_flash_init()`;
- если получает `ESP_ERR_NVS_NO_FREE_PAGES` или `ESP_ERR_NVS_NEW_VERSION_FOUND`, стирает NVS через `nvs_flash_erase()`;
- после erase повторяет `nvs_flash_init()`;
- возвращает итоговый `esp_err_t`.

Это типичный шаблон ESP-IDF.



---

## [089] 04-functions/app_wifi_refresh_status_locked.md

# app_wifi_refresh_status_locked

Исходник: `components/app/src/app_wifi.c`.

`app_wifi_refresh_status_locked()` обновляет IP-адреса в `s_status`.

Что делает:

- если `s_sta_netif` существует, вызывает `esp_netif_get_ip_info()` и пишет `sta_ip`;
- если `s_ap_netif` существует, вызывает `esp_netif_get_ip_info()` и пишет `ap_ip`;
- форматирует IP через `IPSTR` и `IP2STR`.

Слово `locked` в имени сейчас скорее намерение, чем реальная блокировка: mutex здесь не используется.



---

## [090] 04-functions/app_wifi_smoke_run.md

# app_wifi_smoke_run

Исходник: `components/app/src/app_wifi.c`.

## Назначение

`app_wifi_smoke_run()` по смыслу уже является не просто smoke-test, а основной функцией Wi‑Fi bringup. Имя историческое, а роль — вполне центральная.

Именно она подготавливает сетевую среду для будущего HTTP/WebSocket API.

## Что делает функция

- проверяет, включен ли Wi‑Fi stack (`CONFIG_ESP_WIFI_ENABLED` или `CONFIG_ESP_HOST_WIFI_ENABLED`);
- не запускается повторно, если `s_wifi_started == true`;
- инициализирует NVS через `app_wifi_nvs_init_once()`;
- вызывает `esp_netif_init()`;
- создает default event loop через `esp_event_loop_create_default()`;
- создает STA netif через `esp_netif_create_default_wifi_sta()`;
- создает AP netif через `esp_netif_create_default_wifi_ap()`;
- инициализирует Wi‑Fi через `esp_wifi_init()`;
- регистрирует common event handler;
- выбирает режим Wi‑Fi через `app_wifi_pick_mode()`;
- строит AP SSID через `app_wifi_build_ap_ssid()`;
- конфигурирует SoftAP;
- при `CONFIG_APP_WIFI_CONNECT` и непустом SSID конфигурирует STA;
- запускает Wi‑Fi через `esp_wifi_start()`;
- отключает power save через `esp_wifi_set_ps(WIFI_PS_NONE)`;
- обновляет status;
- помечает `s_status.initialized = true` и `s_wifi_started = true`.

## Важная точность по режиму работы

Функция **не всегда** ставит `WIFI_MODE_APSTA`.

Реальное поведение такое:

- если `CONFIG_APP_WIFI_CONNECT` выключен или SSID пустой, выбирается `WIFI_MODE_AP`;
- если STA-подключение включено и SSID задан, выбирается `WIFI_MODE_APSTA`.

Это важно, потому что текущая конфигурация проекта по умолчанию работает именно в AP-only режиме.

## Что функция сейчас НЕ делает

Несмотря на наличие соответствующего helper'а в коде, `app_wifi_smoke_run()` сейчас не вызывает `app_wifi_log_scan_results()` автоматически.

То есть:

- scan-функция существует;
- но список найденных точек доступа при старте автоматически не печатается.

## Ключевой результат

После успешного выполнения функция:

- поднимает сетевую среду;
- делает доступным SoftAP;
- при соответствующей конфигурации инициирует STA-подключение;
- готовит систему к запуску `app_net_start()`.

## Связи

- [[03-components/app_wifi]]
- [[04-functions/app_wifi_nvs_init_once]]
- [[04-functions/app_wifi_build_ap_ssid]]
- [[04-functions/app_net_start]]



---

## [091] 04-functions/i2c_bus_deinit.md

# i2c_bus_deinit

Исходник: `components/i2c_bus/src/i2c_bus.c`.

`i2c_bus_deinit()` освобождает I2C master bus.

Что делает:

- если `s_bus == NULL`, просто выходит;
- вызывает `i2c_del_master_bus(s_bus)`;
- если удаление не удалось, пишет warning;
- при успехе ставит `s_bus = NULL`;
- логирует `bus released`.

Используется перед диагностическим sweep, чтобы временные bus на других GPIO не конфликтовали с основным.



---

## [092] 04-functions/i2c_bus_diag_probe_pair.md

# i2c_bus_diag_probe_pair

Исходник: `components/i2c_bus/src/i2c_bus_diag.c`.

`i2c_bus_diag_probe_pair()` проверяет одну пару SDA/SCL.

Что делает:

- игнорирует пару, если SDA и SCL одинаковые;
- переводит оба GPIO в input;
- читает idle levels;
- создает временный I2C bus;
- проверяет адреса `0x68` и `0x69`;
- если устройство найдено, пишет warning `FOUND`;
- удаляет временный I2C bus.

Функция static, то есть доступна только внутри `i2c_bus_diag.c`.



---

## [093] 04-functions/i2c_bus_diag_sweep_mpu_pairs.md

# i2c_bus_diag_sweep_mpu_pairs

Исходник: `components/i2c_bus/src/i2c_bus_diag.c`.

`i2c_bus_diag_sweep_mpu_pairs()` перебирает набор возможных SDA/SCL пар.

Зачем:

- если MPU не найден на текущих GPIO;
- если провода перепутаны;
- если неизвестно, какие pins реально подключены на плате.

Пары:

- `1/2`, `2/1`;
- `3/2`, `2/3`;
- `1/3`, `3/1`;
- `4/2`, `2/4`;
- `1/4`, `4/1`;
- `10/11`, `11/10`.

Для каждой пары вызывается `i2c_bus_diag_probe_pair()`.



---

## [094] 04-functions/i2c_bus_init.md

# i2c_bus_init

Исходник: `components/i2c_bus/src/i2c_bus.c`.

`i2c_bus_init()` создает I2C master bus.

## Роль в архитектуре

Это входная точка всей I2C-подсистемы. Без успешного `i2c_bus_init()` проект не сможет ни сканировать шину, ни проверять MPU, ни читать телеметрию сенсора.

Что делает:

- если bus уже создан, возвращает `ESP_OK`;
- при включенном selftest вызывает `i2c_bus_selfcheck_gpio()`;
- читает idle levels SDA/SCL через `i2c_bus_read_lines()`;
- логирует уровни;
- если SDA или SCL low в idle, пишет warning;
- заполняет `i2c_master_bus_config_t`;
- вызывает `i2c_new_master_bus(&bus_cfg, &s_bus)`;
- логирует выбранные GPIO и частоту.

Конфиги:

- `CONFIG_I2C_BUS_SDA_GPIO`
- `CONFIG_I2C_BUS_SCL_GPIO`
- `CONFIG_I2C_BUS_FREQ_HZ`

## Что особенно полезно в реализации

Функция не ограничивается просто вызовом `i2c_new_master_bus()`. Перед этим она:

- проверяет idle levels линий;
- может выполнить self-test GPIO;
- предупреждает, если линия удерживается в low.

Это превращает `i2c_bus_init()` в хороший инженерный bringup-инструмент, а не только в thin wrapper над SDK.

## Практический смысл

Если I2C-подсистема не работает, одной из первых функций для анализа всегда будет именно `i2c_bus_init()`, потому что здесь закладываются:

- номера GPIO;
- частота шины;
- базовая проверка линий;
- факт успешного создания bus handle.



---

## [095] 04-functions/i2c_bus_log_lines.md

# i2c_bus_log_lines

Исходник: `components/i2c_bus/src/i2c_bus.c`.

`i2c_bus_log_lines()` печатает уровни SDA/SCL.

Аргументы:

- `where`: подпись места вызова;
- `l`: структура с уровнями `sda` и `scl`.

Используется в `i2c_bus_init()` для ранней диагностики проводки.



---

## [096] 04-functions/i2c_bus_log_scan_table.md

# i2c_bus_log_scan_table

Исходник: `components/i2c_bus/src/i2c_bus.c`.

`i2c_bus_log_scan_table()` компилируется только при включенном `CONFIG_I2C_BUS_SCAN_TABLE`.

Назначение:

- красиво вывести карту адресов I2C;
- показать найденные адреса;
- отметить недопустимые адреса как `..`;
- пустые допустимые адреса как `--`.

Это диагностическая функция. На runtime логику устройств она не влияет.



---

## [097] 04-functions/i2c_bus_open_device.md

# i2c_bus_open_device

Исходник: `components/i2c_bus/src/i2c_bus.c`.

`i2c_bus_open_device()` создает device handle для конкретного I2C адреса.

Что настраивает:

- 7-bit address mode;
- `device_address = addr`;
- `scl_speed_hz = CONFIG_I2C_BUS_FREQ_HZ`;
- ACK check включен.

Функция используется внутри `i2c_bus_read()` и `i2c_bus_write()`.

Это static helper, наружу он не экспортируется.



---

## [098] 04-functions/i2c_bus_probe_addr.md

# i2c_bus_probe_addr

Исходник: `components/i2c_bus/src/i2c_bus.c`.

`i2c_bus_probe_addr()` проверяет, отвечает ли устройство на конкретном I2C адресе.

Что делает:

- если bus не создан, возвращает `ESP_ERR_INVALID_STATE`;
- вызывает `i2c_master_probe(s_bus, addr, I2C_XFER_TIMEOUT_MS)`.

Используется в `mpu9250_probe_addr()` для проверки адресов `0x68` и `0x69`.



---

## [099] 04-functions/i2c_bus_read.md

# i2c_bus_read

Исходник: `components/i2c_bus/src/i2c_bus.c`.

`i2c_bus_read()` читает данные из регистра I2C устройства.

Аргументы:

- `addr`: I2C адрес устройства;
- `reg`: адрес регистра внутри устройства;
- `out`: куда писать результат;
- `out_len`: сколько байт читать.

Алгоритм:

- проверяет, что bus создан;
- проверяет аргументы;
- открывает device handle через `i2c_bus_open_device()`;
- вызывает `i2c_master_transmit_receive()`;
- удаляет device handle;
- возвращает ошибку чтения или ошибку удаления handle, если чтение было успешным.

Это основной путь чтения MPU registers.



---

## [100] 04-functions/i2c_bus_read_lines.md

# i2c_bus_read_lines

Исходник: `components/i2c_bus/src/i2c_bus.c`.

`i2c_bus_read_lines()` временно читает уровни SDA/SCL как обычные GPIO inputs.

Что делает:

- ставит SDA GPIO в input;
- ставит SCL GPIO в input;
- читает уровни через `gpio_get_level()`;
- возвращает структуру `i2c_lines_t`.

Используется до создания I2C peripheral, чтобы проверить idle состояние линий.



---

## [101] 04-functions/i2c_bus_scan.md

# i2c_bus_scan

Исходник: `components/i2c_bus/src/i2c_bus.c`.

`i2c_bus_scan()` выполняет диагностическое обнаружение устройств на шине I2C. В контексте этого проекта функция особенно важна, потому что она позволяет быстро понять, «жива» ли шина вообще и отвечает ли MPU на ожидаемых адресах.

## Роль функции в проекте

Сканирование I2C здесь — не декоративная возможность, а часть реальной процедуры самопроверки устройства при старте. До того как приложение начнет красиво печатать телеметрию MPU, нужно понять более базовую вещь: есть ли вообще ответ по шине.

Поэтому `i2c_bus_scan()` помогает отличить несколько классов проблем:

- датчик физически не подключен;
- перепутаны SDA/SCL;
- выбраны неверные GPIO в `sdkconfig`;
- отсутствуют подтяжки;
- устройство сидит на адресе `0x69` вместо `0x68`;
- шина инициализирована, но конкретный сенсор не отвечает.

## Как работает функция

Алгоритм можно описать так:

1. Проверяется, инициализирована ли шина (`s_bus`).
2. На время сканирования уменьшается шум низкоуровневых логов `i2c.master`.
3. Выполняется приоритетная проверка адресов MPU — `0x68` и `0x69`.
4. Если включен `CONFIG_I2C_BUS_SCAN_FULL`, сканируется полный диапазон адресов `0x03..0x77`.
5. По ходу сканирования считаются успешные ответы, timeout'ы и прочие ошибки.
6. При включенном `CONFIG_I2C_BUS_SCAN_TABLE` выводится табличное представление найденных адресов.
7. Если не найдено ничего, пользователю выводятся практические подсказки по проводке и питанию.

Такой подход дает баланс между скоростью и полнотой: сначала проверяются наиболее вероятные адреса нужного датчика, а уже потом — вся шина при необходимости.

## Почему сначала проверяются 0x68 и 0x69

В этом проекте целевой сенсор — MPU9250/совместимое устройство. Для него наиболее ожидаемыми являются именно эти два адреса. Поэтому быстрый targeted probe имеет смысл:

- сокращает время диагностики;
- быстрее дает ответ в типовом случае;
- уменьшает шум в логах;
- помогает раннему стартовому анализу в `app_init()`.

Это хороший пример инженерной оптимизации под конкретный стенд.

## Как читать результаты

С точки зрения эксплуатации результаты `i2c_bus_scan()` можно трактовать так:

- найден `0x68` или `0x69` — шина, вероятно, исправна и датчик присутствует;
- найдено другое устройство, но не MPU — проводка шины жива, но целевой сенсор не отвечает;
- нет ни одного адреса — вероятнее всего проблема в питании, распиновке или подтяжках;
- много timeout/error — возможна нестабильная физика линии или неверная конфигурация GPIO/частоты.

## Почему функция не переводит SDA/SCL в обычный GPIO

Это важное проектное решение. Во время scan код не «отцепляет» аппаратную I2C периферию, переводя линии в plain GPIO для дополнительных тестов. Иначе можно было бы получить ложные эффекты и нарушить нормальную работу уже поднятой шины.

То есть функция остается в рамках корректной модели работы I2C-контроллера, а не пытается любой ценой провести грубую низкоуровневую диагностику поверх активной периферии.

## Практическая ценность для лабораторной установки

`i2c_bus_scan()` особенно полезна на этапе сборки стенда и первичного bringup:

- позволяет быстро подтвердить, что выбранные пины действительно рабочие;
- помогает перед началом чтения регистров MPU;
- делает стартовые логи самодостаточными для удаленного анализа;
- снижает время на поиск банальных аппаратных ошибок.

Для курсовой это можно описывать как встроенный механизм аппаратно-программной самодиагностики шины датчиков.

См. также:

- [[04-functions/i2c_bus_init]]
- [[04-functions/mpu9250_probe_and_read_whoami]]
- [[03-components/i2c_bus]]



---

## [102] 04-functions/i2c_bus_selfcheck_gpio.md

# i2c_bus_selfcheck_gpio

Исходник: `components/i2c_bus/src/i2c_bus.c`.

`i2c_bus_selfcheck_gpio()` компилируется только при включенном `CONFIG_I2C_BUS_SELFTEST`.

Что проверяет:

- idle уровни SDA/SCL;
- возможность утянуть SCL в low;
- возврат SCL обратно в high.

Зачем:

- обнаружить проблемы с проводкой;
- увидеть, что линия зажата в low;
- проверить pull-up поведение до старта I2C peripheral.



---

## [103] 04-functions/i2c_bus_write.md

# i2c_bus_write

Исходник: `components/i2c_bus/src/i2c_bus.c`.

`i2c_bus_write()` пишет данные в регистр I2C устройства.

Аргументы:

- `addr`: I2C адрес устройства;
- `reg`: адрес регистра;
- `data`: данные;
- `len`: длина данных.

Ограничение:

- максимум 16 байт данных за один вызов, потому что локальный буфер `uint8_t buf[1 + 16]`.

Алгоритм:

- проверяет bus;
- проверяет аргументы;
- кладет `reg` в первый байт буфера;
- копирует data после него;
- открывает device handle;
- вызывает `i2c_master_transmit()`;
- удаляет device handle.



---

## [104] 04-functions/mpu9250_probe_addr.md

# mpu9250_probe_addr

Исходник: `components/mpu9250/src/mpu9250.c`.

`mpu9250_probe_addr()` ищет MPU на адресах `0x68` и `0x69`.

Что делает:

- проверяет `out_addr`;
- вызывает `i2c_bus_probe_addr(addr)` для `0x68`;
- если успех, записывает адрес и возвращает `ESP_OK`;
- затем пробует `0x69`;
- если ни один адрес не ответил, возвращает `ESP_ERR_NOT_FOUND`.

Почему только два адреса:

- MPU9250 обычно выбирает адрес через AD0 pin;
- стандартные варианты адреса: `0x68` или `0x69`.



---

## [105] 04-functions/mpu9250_probe_and_read_whoami.md

# mpu9250_probe_and_read_whoami

Исходник: `components/mpu9250/src/mpu9250.c`.

`mpu9250_probe_and_read_whoami()` объединяет поиск адреса и чтение WHO_AM_I.

## Роль в архитектуре

Это ключевая связующая функция между I2C-обнаружением устройства и верхними слоями, которым уже не хочется отдельно думать о probe и отдельно о register read.

Алгоритм:

- проверяет выходные указатели;
- вызывает `mpu9250_probe_addr(out_addr)`;
- если адрес не найден, возвращает ошибку;
- вызывает `mpu9250_read_whoami(*out_addr, out_whoami)`.

Используется в:

- `app_mpu_whoami_check()`;
- `app_mpu_pretty_init()`.

## Почему функция удобна

Она инкапсулирует типовой сценарий "найти устройство и сразу идентифицировать его" в одном вызове. За счет этого:

- код в верхних слоях короче;
- меньше шансов забыть второй шаг после успешного probe;
- проще логировать результат как единое действие.

## Практический смысл

Если эта функция завершается ошибкой, то проблема обычно лежит в одном из трех мест:

- устройство не найдено по адресам `0x68/0x69`;
- I2C-шина работает некорректно;
- устройство найдено, но чтение `WHO_AM_I` не удалось.

Поэтому это одна из самых полезных функций для ранней диагностики MPU-подсистемы.



---

## [106] 04-functions/mpu9250_read_whoami.md

# mpu9250_read_whoami

Исходник: `components/mpu9250/src/mpu9250.c`.

`mpu9250_read_whoami()` читает регистр `WHO_AM_I`.

Что делает:

- проверяет `out_whoami`;
- пишет `0x00` в `MPU_REG_PWR_MGMT_1`;
- читает один байт из `MPU_REG_WHO_AM_I`;
- возвращает результат `i2c_bus_read()`.

Запись в `PWR_MGMT_1` нужна, чтобы разбудить MPU перед чтением.



---

## [107] 04-functions/mpu9250_whoami_name.md

# mpu9250_whoami_name

Исходник: `components/mpu9250/src/mpu9250.c`.

`mpu9250_whoami_name()` переводит значение WHO_AM_I в строку.

Поддерживаемые значения:

- `0x70`: `MPU-6500`;
- `0x71`: `MPU-9250`;
- `0x73`: `MPU-9255/variant`;
- другое: `unknown/clone`.

Это диагностическая функция для логов и telemetry.



---

## [108] 05-config/App Kconfig.md

# App Kconfig

Файл: `components/app/Kconfig`.

`components/app/Kconfig` — это центральная точка compile-time конфигурирования прикладной логики проекта. Именно здесь задаются те параметры, которые превращают один и тот же код в разные варианты стенда: с разным режимом работы, сетью, телеметрией и управлением шаговым двигателем.

## Почему этот файл важен

В ESP-IDF `Kconfig` — это не просто «набор флагов». Это механизм формализации проектных решений. Через него приложение явно описывает:

- какие функциональные ветки включены;
- какие параметры аппаратуры используются;
- какой сценарий запуска ожидается;
- какие сетевые возможности доступны.

Для документации это особенно полезно: можно отделить изменяемую конфигурацию от неизменной логики исходников.

## Основные группы настроек

В файле сосредоточены несколько логических блоков:

- режим приложения (`app mode`);
- logging и tick-поведение;
- Wi‑Fi bringup;
- параметры SoftAP;
- параметры STA;
- включение HTTP/WebSocket API;
- настройки stepper/L293D.

То есть это конфигурация именно прикладного уровня, а не периферийного ядра ESP-IDF.

## APP_MODE

`APP_MODE` определяет, какой сценарий считается основным для данного билда. В текущей конфигурации фигурируют варианты:

- `APP_MODE_MPU9250`;
- `APP_MODE_L293D_TEST`.

Даже если фактически в приложении могут использоваться сразу несколько подсистем, наличие такого режима полезно как проектный маркер: он показывает, какой use-case был главным при данной сборке.

## Tick logging и runtime-наблюдаемость

Отдельная группа опций управляет тем, насколько подробно главный цикл приложения печатает текущую информацию о состоянии. Это важно для лабораторного стенда, потому что через лог можно быстро понять:

- жив ли `app_tick()`;
- обновляется ли телеметрия;
- виден ли датчик;
- идет ли сетевое обслуживание.

Слишком подробный лог увеличивает шум, но на этапе bringup и демонстрации он полезен.

## Wi‑Fi bringup

Ключевые опции сетевого запуска:

- `APP_WIFI_SMOKE` — поднимать ли Wi‑Fi на старте вообще;
- `APP_WIFI_CONNECT` — пытаться ли подключаться к внешнему роутеру в режиме STA;
- `APP_NET_ENABLE` — публиковать ли HTTP/WebSocket API.

Вместе эти три опции задают сценарий сетевой жизни приложения:

- полностью локальный embedded режим без сети;
- режим точки доступа для прямого подключения к плате;
- смешанный режим AP+STA с попыткой выхода в инфраструктурную сеть.

## Настройки SoftAP

Группа параметров точки доступа управляет тем, как плата видна внешнему клиенту:

- `APP_WIFI_AP_SSID_PREFIX` — имя/префикс SSID;
- `APP_WIFI_AP_PASSWORD` — пароль точки доступа;
- `APP_WIFI_AP_CHANNEL` — радиоканал;
- `APP_WIFI_SCAN_MAX_AP` — ограничение на число записей при scan.

Это важно не только для работы, но и для UX лабораторного стенда: пользователь должен понимать, как найти устройство и как к нему подключиться.

## Настройки STA

Если включен `APP_WIFI_CONNECT`, используются:

- `APP_WIFI_SSID`;
- `APP_WIFI_PASSWORD`.

Эти параметры переводят устройство из режима изолированной точки доступа в режим, способный подключаться к существующей Wi‑Fi инфраструктуре. В текущем проекте это опциональный путь, а не обязательный сценарий.

## Параметры stepper/L293D

Отдельный крупный блок настроек определяет аппаратное соответствие и временные параметры шагового двигателя:

- `APP_L293D_IN1_GPIO`
- `APP_L293D_IN2_GPIO`
- `APP_L293D_IN3_GPIO`
- `APP_L293D_IN4_GPIO`
- `APP_L293D_STEP_DELAY_MS`
- `APP_STEPPER_UART_BAUD_RATE`
- `APP_STEPPER_LED_ENABLE`
- `APP_STEPPER_LED_GPIO`

Через эти опции код не «зашивает» распиновку намертво, а позволяет перенести приложение на другой стенд или иную разводку с минимальными изменениями.

## Почему Kconfig здесь особенно удобен

Для данного проекта `Kconfig` полезен по трем причинам:

1. Отделяет аппаратные и режимные параметры от логики функций.
2. Позволяет менять сценарий работы без переписывания исходников.
3. Делает конфигурацию обозримой через `menuconfig` и `sdkconfig`.

Для курсовой это можно подать как механизм параметризации embedded-приложения на этапе сборки.

См. также:

- [[05-config/Configuration overview]]
- [[05-config/Current network configuration]]
- [[03-components/app component]]



---

## [109] 05-config/CMake overview.md

# CMake overview

ESP-IDF использует CMake, но компоненты объявляются через `idf_component_register`.

Корневой `CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.16)
include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(p4_lab)
```

`main/CMakeLists.txt` регистрирует `main.c`.

`components/app/CMakeLists.txt` регистрирует прикладные C-файлы и зависимости:

- `i2c_bus`;
- `mpu9250`;
- `esp_driver_gpio`;
- `esp_driver_uart`;
- `esp_wifi`;
- `esp_event`;
- `esp_http_server`;
- `esp_netif`;
- `nvs_flash`.

`components/i2c_bus/CMakeLists.txt` регистрирует I2C sources и private dependencies.

`components/mpu9250/CMakeLists.txt` регистрирует MPU source и зависит от `i2c_bus`.



---

## [110] 05-config/Configuration overview.md

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



---

## [111] 05-config/Current network configuration.md

# Current network configuration

Эта страница фиксирует не абстрактные возможности сетевой подсистемы, а текущий фактический профиль сети, собранный из `sdkconfig` проекта.

## Активные настройки

```text
CONFIG_ESP_HOST_WIFI_ENABLED=y
CONFIG_HTTPD_WS_SUPPORT=y
CONFIG_APP_WIFI_SMOKE=y
CONFIG_APP_WIFI_AP_SSID_PREFIX="JC-ESP32P4M3"
CONFIG_APP_WIFI_AP_PASSWORD="esp32p4m3"
CONFIG_APP_WIFI_AP_CHANNEL=1
CONFIG_APP_WIFI_SCAN_MAX_AP=20
# CONFIG_APP_WIFI_CONNECT is not set
CONFIG_APP_NET_ENABLE=y
```

## Что это означает в реальном runtime

Эта конфигурация задает вполне конкретный сценарий поведения устройства после загрузки:

1. Сетевой стек Wi‑Fi в проекте включен.
2. При старте выполняется Wi‑Fi bringup (`CONFIG_APP_WIFI_SMOKE=y`).
3. Плата поднимает собственную точку доступа.
4. HTTP/WebSocket API включен.
5. Подключение к внешнему роутеру в STA-режиме не выполняется.

Иными словами, текущая сборка ориентирована на прямое подключение пользователя к самой плате, а не на встраивание платы в уже существующую Wi‑Fi сеть.

## Практический профиль сети

С точки зрения эксплуатации это означает следующее:

- основная модель доступа — подключиться к SoftAP платы;
- после подключения можно обращаться к REST API и WebSocket напрямую;
- внешний роутер не нужен для базовой демонстрации;
- поведение хорошо подходит для стенда, который должен быть самодостаточным в лабораторных условиях.

Это удобно для отладки и защиты работы: устройство не зависит от инфраструктуры аудитории или лаборатории.

## Роль отдельных параметров

### `CONFIG_ESP_HOST_WIFI_ENABLED`

Показывает, что в проекте активен host Wi‑Fi path, необходимый для работы сетевой части на текущей платформе/стеке.

### `CONFIG_HTTPD_WS_SUPPORT`

Разрешает WebSocket endpoint и периодическую push-телеметрию. Без этой опции проект бы сохранил HTTP API, но потерял бы удобный потоковый канал обновлений.

### `CONFIG_APP_WIFI_SMOKE`

Означает, что подъем Wi‑Fi происходит автоматически на старте приложения. Пользователь не должен вручную инициировать сетевой bringup после загрузки.

### `CONFIG_APP_WIFI_AP_SSID_PREFIX`

Задает префикс имени точки доступа. На практике это часть пользовательского интерфейса устройства: по этому имени пользователь ищет плату в списке Wi‑Fi сетей.

### `CONFIG_APP_WIFI_AP_PASSWORD`

Пароль для входа в SoftAP. Для лабораторной среды это упрощает подключение, но в более серьезном deployment-профиле мог бы потребоваться иной security policy.

### `CONFIG_APP_WIFI_AP_CHANNEL`

Фиксирует радиоканал AP. Это может быть важно при работе в зашумленной среде или при наличии требований к совместимости/устойчивости.

### `CONFIG_APP_WIFI_SCAN_MAX_AP`

Ограничивает объем результатов scan, если scan выполняется. Это не означает, что scan всегда происходит автоматически, но ограничивает ожидаемую диагностическую нагрузку.

### `CONFIG_APP_WIFI_CONNECT` отключен

Это ключевой факт текущей сборки. Значит устройство не должно ожидать получение `sta_ip` как основной рабочий путь. Основной сетевой интерфейс — именно AP.

### `CONFIG_APP_NET_ENABLE`

Включает прикладной HTTP/WebSocket API. Без этой опции Wi‑Fi мог бы быть поднят только как транспорт, без пользовательского сетевого интерфейса.

## Вывод

Текущая конфигурация — это автономный AP-first профиль: плата сама создает сеть, пользователь подключается к ней напрямую, после чего получает доступ к API и телеметрии без необходимости UART и без зависимости от внешнего роутера.

Для курсовой это хороший пример автономной беспроводной диагностико-управляющей подсистемы embedded-стенда.

См. также:

- [[06-operations/Runtime WiFi verification without UART]]
- [[06-operations/How to enable STA WiFi]]
- [[02-architecture/WiFi HTTP WebSocket architecture]]



---

## [112] 05-config/Header files.md

# Header files

Публичные header files в проекте задают границы между компонентами и фиксируют их контракты. Именно по ним видно, какие возможности модуль предоставляет наружу и какие детали реализации он, наоборот, скрывает.

Для архитектурного анализа это очень важный слой: если `.c` файлы показывают внутреннюю механику, то `.h` файлы показывают официальную модель взаимодействия между компонентами.

## Почему заголовки важны

Хорошо спроектированный header отвечает на три вопроса:

1. Что модуль умеет делать?
2. Какие структуры данных он экспортирует наружу?
3. Что другим компонентам знать не нужно?

В этом проекте заголовки в целом выполняют именно эту роль: дают достаточно API для композиции системы, но не раскрывают все внутренние статические переменные и служебные helpers.

## `app.h`

Основной фасад всего приложения:

- `app_init()`;
- `app_tick()`;
- `app_tick_delay_ms()`.

Это самый верхний уровень API. `main.c` практически ничего не знает о внутренних подсистемах и работает именно через этот минимальный интерфейс. Такой подход сохраняет `main` тонким и архитектурно чистым.

## `app_wifi.h`

Экспортирует сетевую подсистему Wi‑Fi как отдельный сервис:

- `app_wifi_status_t`;
- `app_wifi_smoke_run()`;
- `app_wifi_get_status()`.

Здесь особенно заметно разделение на команды и состояние: одна функция отвечает за bringup, другая — за чтение статуса, а структура `app_wifi_status_t` формализует наблюдаемую модель Wi‑Fi для остальных частей программы.

## `app_net.h`

Минимальный контракт сетевого API:

- `app_net_start()`;
- `app_net_tick()`.

Это означает, что внешним компонентам не нужно знать детали маршрутов, JSON builder'ов и WebSocket send queue. Для orchestration-слоя достаточно знать только две вещи: как запустить сетевой API и как периодически его обслуживать.

## `app_stepper.h`

Определяет границу модуля управления шаговым двигателем:

- `app_stepper_snapshot_t`;
- `app_stepper_init()`;
- `app_stepper_tick()`;
- `app_stepper_command_char()`;
- `app_stepper_get_snapshot()`.

Этот набор особенно удачен архитектурно, потому что покрывает все четыре аспекта подсистемы:

- инициализация;
- периодическое исполнение;
- прием команд;
- чтение состояния.

То есть header буквально фиксирует полный жизненный цикл stepper-модуля.

## `i2c_bus.h`

Заголовок low-level шины, который экспортирует операции:

- init/deinit;
- scan;
- probe;
- register read/write и смежные действия.

Этот файл важен тем, что прячет детали работы с конкретным драйвером ESP-IDF и дает прикладному коду более узкий и понятный интерфейс для работы с I2C-устройствами.

## `mpu9250.h`

Минимальный публичный интерфейс для работы с MPU-идентификацией и базовым чтением WHO_AM_I.

Это не полноценный драйвер со всем набором режимов MPU, а компактный helper API, достаточный для задач текущего проекта: обнаружить устройство, подтвердить его тип и использовать это как основу дальнейшей телеметрии.

## Что видно по заголовкам о стиле проекта

По структуре header files можно сделать несколько выводов о проекте:

- архитектура модульная, без лишней логики в `main`;
- есть разделение между orchestration, networking, sensor bus и actuator control;
- наружу экспортируется состояние в виде snapshot/status структур;
- многие внутренние helpers сознательно скрыты внутри `.c` файлов.

Для курсовой это хороший аргумент в пользу того, что проект строится на принципах модульности и слабой связанности.

См. также:

- [[00-index/Source map]]
- [[03-components/app component]]
- [[03-components/app_net]]
- [[03-components/app_stepper]]



---

## [113] 05-config/I2C Kconfig.md

# I2C Kconfig

Файл: `components/i2c_bus/Kconfig`.

`I2C Kconfig` задает аппаратную конфигурацию общей шины датчиков. В этом проекте через нее подключается MPU, поэтому от корректности этих настроек зависит не просто работа вспомогательного модуля, а весь канал получения инерциальной телеметрии.

## Какие параметры определяются

Основные опции:

- `I2C_BUS_SDA_GPIO` — номер GPIO, используемого как SDA;
- `I2C_BUS_SCL_GPIO` — номер GPIO, используемого как SCL;
- `I2C_BUS_FREQ_HZ` — тактовая частота шины I2C.

На первый взгляд параметров немного, но это как раз тот случай, когда три настройки определяют почти всю судьбу подсистемы.

## Текущие значения проекта

По данным `sdkconfig` сейчас используются:

- `CONFIG_I2C_BUS_SDA_GPIO=1`
- `CONFIG_I2C_BUS_SCL_GPIO=2`
- `CONFIG_I2C_BUS_FREQ_HZ=100000`

Это и есть текущая аппаратная привязка к стенду.

## Что означает выбор частоты 100 кГц

`100000` Гц — стандартный режим I2C ($100\,kHz$). Для лабораторного проекта это разумный и безопасный выбор, потому что он:

- лучше переносит неидеальную проводку;
- уменьшает вероятность ошибок на длинных/шумных линиях;
- подходит для начальной диагностики датчика;
- обычно достаточен по пропускной способности для периодического чтения MPU.

То есть текущая конфигурация оптимизирована скорее на надежный bringup, чем на максимальную скорость обмена.

## Почему эти параметры стоит держать в Kconfig

Если бы SDA/SCL и частота были захардкожены в C-коде, перенос проекта на другую плату или эксперимент с новой разводкой превращался бы в правку исходников. Kconfig делает это изменением конфигурации сборки, а не логики.

Это особенно полезно, когда:

- меняется плата/ревизия стенда;
- нужно быстро проверить альтернативную пару GPIO;
- надо понизить частоту для диагностики нестабильной шины;
- проект развивается от прототипа к более устойчивой аппаратной версии.

## Какие ошибки обычно связаны с этими опциями

Неверные параметры здесь проявляются очень характерно:

- неправильные SDA/SCL — сканирование ничего не находит;
- слишком агрессивная частота — появляются timeout/error на scan/read;
- несовместимая распиновка — WHO_AM_I probe не подтверждает датчик;
- частичная аппаратная проблема — шина поднимается, но чтение нестабильно.

Поэтому `I2C Kconfig` тесно связан с ранней диагностикой через `i2c_bus_init()` и `i2c_bus_scan()`.

## Практический смысл для документации

Эту страницу полезно рассматривать как мост между схемой подключения и программной частью. Здесь фиксируется, на какие физические линии рассчитан код и в каком режиме ожидается работа шины датчика.

См. также:

- [[04-functions/i2c_bus_init]]
- [[04-functions/i2c_bus_scan]]
- [[03-components/i2c_bus]]



---

## [114] 05-config/sdkconfig.defaults.md

# sdkconfig.defaults

Файл: `sdkconfig.defaults`.

Содержит baseline:

```text
CONFIG_LOG_DEFAULT_LEVEL_INFO=y
CONFIG_ESP_CONSOLE_UART_DEFAULT=y
CONFIG_HTTPD_WS_SUPPORT=y
```

Зачем это важно:

- `CONFIG_HTTPD_WS_SUPPORT=y` нужен для `/ws`;
- `CONFIG_ESP_CONSOLE_UART_DEFAULT=y` сохраняет UART console behavior;
- default log level info помогает видеть bringup без слишком шумного debug.

Если удалить `CONFIG_HTTPD_WS_SUPPORT=y`, WebSocket endpoint не будет корректно доступен в сборке.



---

## [115] 05-config/sdkconfig.md

# sdkconfig

Файл: `sdkconfig`.

`sdkconfig` - сгенерированное состояние конфигурации ESP-IDF. Его обычно не редактируют руками, но он важен для понимания текущей сборки.

Важные текущие значения:

- target: `CONFIG_IDF_TARGET="esp32p4"`;
- Wi-Fi для ESP32-P4 через host Wi-Fi: `CONFIG_ESP_HOST_WIFI_ENABLED=y`;
- WebSocket support: `CONFIG_HTTPD_WS_SUPPORT=y`;
- console UART: `CONFIG_ESP_CONSOLE_UART_DEFAULT=y`;
- LWIP sockets: `CONFIG_LWIP_MAX_SOCKETS=10`;
- app mode: `CONFIG_APP_MODE_L293D_TEST=y`;
- Wi-Fi bringup: `CONFIG_APP_WIFI_SMOKE=y`;
- HTTP/WebSocket API: `CONFIG_APP_NET_ENABLE=y`;
- SoftAP SSID prefix: `CONFIG_APP_WIFI_AP_SSID_PREFIX="JC-ESP32P4M3"`;
- SoftAP password: `CONFIG_APP_WIFI_AP_PASSWORD="esp32p4m3"`;
- SoftAP channel: `CONFIG_APP_WIFI_AP_CHANNEL=1`;
- STA connect: `# CONFIG_APP_WIFI_CONNECT is not set`.

Если нужно подключать ESP к домашнему Wi-Fi как STA, включи `APP_WIFI_CONNECT` и задай SSID/password через `idf.py menuconfig`.



---

## [116] 06-operations/API examples.md

# API examples

## Назначение API

Сетевой API проекта нужен для двух вещей:

- читать текущее состояние прошивки;
- передавать команды управления шаговым двигателем.

В текущем виде API достаточно прост, чтобы его можно было использовать:

- вручную через `curl`;
- из web-приложения;
- из тестового скрипта;
- как источник примеров для описания в курсовой.

Базовый адрес при работе через SoftAP:

```text
http://192.168.4.1
```

## Получить Wi‑Fi status

```bash
curl http://192.168.4.1/api/wifi
```

Типичный смысл ответа:

- инициализирован ли Wi‑Fi;
- поднят ли SoftAP;
- пытался ли модуль подключаться как STA;
- какой IP сейчас у AP/STA.

## Получить общую телеметрию

```bash
curl http://192.168.4.1/api/telemetry
```

Это главный endpoint. Он возвращает сводное состояние по разделам:

- `system`
- `mpu`
- `i2c`
- `stepper`
- `wifi`

Именно этот endpoint удобнее всего использовать как основу для будущего web-dashboard.

## Команды управления двигателем

### Остановить мотор

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"s"}'
```

### Запустить вперед

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"f"}'
```

### Запустить назад

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"r"}'
```

### Включить режим sweep

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"w"}'
```

### Один шаг вперед

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"1"}'
```

### Один шаг назад

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"2"}'
```

### Ускорить

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"+"}'
```

### Замедлить

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"-"}'
```

### Освободить катушки

```bash
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"z"}'
```

## Упрощенный формат body

В текущем коде поддерживается не только JSON, но и короткое текстовое тело. Например:

```bash
curl -X POST http://192.168.4.1/api/command -d 's'
```

Это удобно для ручной проверки API и для минималистичных клиентов.

## Что возвращает `POST /api/command`

После успешного выполнения команда не просто отвечает `OK`, а возвращает актуальную телеметрию через тот же механизм, что и `GET /api/telemetry`.

Это удобно, потому что клиент сразу получает обновленное состояние системы после команды.

## WebSocket

Для постоянного соединения используется endpoint:

```text
ws://192.168.4.1/ws
```

Через него можно:

- отправлять те же команды;
- получать обновления состояния раз в секунду.

## Почему это полезно для курсовой

Этот раздел дает готовые практические примеры взаимодействия с embedded-устройством по сети. Их можно использовать:

- как примеры API-запросов;
- как основу для описания REST/WebSocket интерфейса;
- как доказательство прикладной ценности проекта.



---

## [117] 06-operations/Build and verification.md

# Build and verification

## Цель раздела

Этот раздел нужен не только как инструкция по сборке, но и как фиксация того, что именно уже было проверено на проекте.

## Как устроена сборка в проекте

Проект собирается стандартным способом для ESP-IDF через `idf.py build`.

В рабочем пространстве уже есть настроенная задача сборки, которая:

- переходит в корень проекта;
- экспортирует `IDF_PATH`;
- подгружает окружение через `export.sh`;
- запускает `idf.py build`.

То есть базовый сценарий сборки в этом репозитории уже оформлен и повторяем.

## Фактическая проверка в этой сессии

Во время этой работы сборка была реально запущена через настроенную задачу проекта.

Результат:

```text
Project build complete.
```

Также сборка сообщила:

- размер `p4_lab.bin`: `0xa6dc0` байт;
- свободно в app partition: `0x59240` байт (`35%`);
- bootloader binary size: `0x5a30` байт.

Это уже не теоретическая оценка, а реальный результат текущего состояния проекта.

## Что подтверждает успешная сборка

Успешная сборка подтверждает, что:

- исходники в текущем состоянии компилируются;
- зависимости компонентов корректно разрешаются;
- `app`, `i2c_bus` и `mpu9250` зарегистрированы правильно;
- сетевые зависимости (`esp_http_server`, `esp_wifi`, `esp_netif`, `nvs_flash`) доступны;
- код stepper, Wi‑Fi и HTTP/WebSocket совместим по символам и заголовкам;
- `sdkconfig` согласован с кодом на уровне сборки.

## Что сборка НЕ подтверждает

Успешный `build` не означает автоматом, что всё проверено на железе.

Сборка не подтверждает:

- что плата реально стартует без рантайм-ошибок;
- что Wi‑Fi SoftAP поднялся на живом устройстве;
- что внешний клиент смог подключиться;
- что `HTTP` и `WebSocket` действительно отвечают;
- что двигатель подключен корректно и физически вращается;
- что MPU отвечает на шине с текущей разводкой.

Поэтому после сборки нужны отдельные этапы прошивки и runtime-проверки.

## Что проверять после прошивки

Минимальный practical checklist после загрузки прошивки на устройство:

1. устройство загружается без crash;
2. появляется Wi‑Fi сеть с ожидаемым SSID;
3. `GET /api/wifi` отвечает корректным JSON;
4. `GET /api/telemetry` отдает полную сводку;
5. `POST /api/command` меняет состояние двигателя;
6. WebSocket-клиент получает периодические обновления;
7. если MPU подключен, в телеметрии есть валидные поля по `mpu`.

## Примеры runtime-проверки по сети

После прошивки и подключения к SoftAP можно использовать такие запросы:

```bash
curl http://192.168.4.1/api/wifi
curl http://192.168.4.1/api/telemetry
curl -X POST http://192.168.4.1/api/command -H 'Content-Type: application/json' -d '{"command":"s"}'
```

## Почему этот раздел важен для курсовой

Он позволяет явно разделить:

- compile-time verification;
- deployment;
- runtime verification.

Это хорошая инженерная практика и хороший материал для описания жизненного цикла embedded-проекта: код не просто написан, а проходит последовательные стадии проверки.



---

## [118] 06-operations/How to enable STA WiFi.md

# How to enable STA WiFi

## Текущее состояние проекта

Сейчас проект по умолчанию работает как автономная точка доступа. Подключение к внешнему роутеру в режиме STA выключено:

```text
# CONFIG_APP_WIFI_CONNECT is not set
```

Это означает, что в типовой конфигурации устройство поднимает собственный SoftAP и не пытается подключаться к существующей Wi‑Fi сети.

## Зачем включать STA-режим

STA-режим нужен, если требуется:

- включить ESP в уже существующую локальную сеть;
- обращаться к устройству не только через `192.168.4.1`, но и по IP от роутера;
- интегрировать устройство в более общий стенд;
- не переключаться вручную на SoftAP ESP каждый раз.

## Как включить STA-подключение

Открыть конфигурацию проекта:

```bash
idf.py menuconfig
```

Дальше в разделе `app`:

- включить `attempt Wi-Fi connect after scan`;
- задать `Wi-Fi SSID`;
- задать `Wi-Fi password`;
- сохранить конфигурацию;
- пересобрать проект;
- прошить устройство.

## Что изменится после этого

После включения `CONFIG_APP_WIFI_CONNECT` и задания SSID/PASSWORD функция `app_wifi_smoke_run()` начнет:

- создавать и AP, и STA интерфейсы;
- выбирать режим `WIFI_MODE_APSTA`;
- оставлять SoftAP активным;
- конфигурировать клиентское подключение к роутеру;
- при `WIFI_EVENT_STA_START` вызывать `esp_wifi_connect()`;
- при `WIFI_EVENT_STA_DISCONNECTED` выполнять retry до лимита;
- при `IP_EVENT_STA_GOT_IP` сохранять `sta_ip`.

То есть устройство сохранит автономный способ подключения через свой AP, но одновременно сможет войти в внешнюю сеть.

## Почему SoftAP при этом не пропадает

Это важная особенность архитектуры проекта. Здесь не делается переключение “или AP, или STA”. Вместо этого используется режим `APSTA`, если конфигурация это позволяет.

Преимущества такого решения:

- UART и SoftAP остаются fallback-инструментами;
- проект удобнее демонстрировать;
- снижение зависимости от внешней сети;
- проще вернуть контроль над устройством даже при проблемах с роутером.

## Что проверить после включения STA

После прошивки полезно проверить:

1. точка доступа ESP по-прежнему поднимается;
2. в `/api/wifi` поле `staAttempted` стало `true`;
3. после успешного подключения `staConnected == true`;
4. появилось ненулевое `staIp`;
5. командами API по-прежнему можно управлять устройством.

## Ограничение текущей реализации

Хотя в `app_wifi.c` есть функция `app_wifi_log_scan_results()`, она сейчас не вызывается автоматически. Поэтому включение STA не означает, что проект уже печатает полноценный список найденных сетей при загрузке. Подключение работает, но расширенная визуализация scan пока не встроена в runtime-сценарий.

См. также:

- [[03-components/app_wifi]]
- [[04-functions/app_wifi_event_handler_common]]
- [[06-operations/Runtime WiFi verification without UART]]



---

## [119] 06-operations/Runtime WiFi verification without UART.md

# Runtime WiFi verification without UART

## Зачем нужен такой сценарий

Обычный путь отладки embedded-прошивки — открыть serial monitor и читать логи. Но для этого проекта важно уметь проверить систему и без UART, потому что одна из целей прошивки — дать самодостаточный сетевой интерфейс наблюдения и управления.

Проверка без UART означает: не читать serial monitor, а проверять устройство исключительно через сеть.

## Базовый сценарий проверки

1. Прошить ESP.
2. Подождать завершения загрузки.
3. Найти Wi‑Fi сеть с префиксом `JC-ESP32P4M3`.
4. Подключиться к ней паролем `esp32p4m3`.
5. Открыть `http://192.168.4.1/api/wifi`.
6. Открыть `http://192.168.4.1/api/telemetry`.
7. Отправить управляющую команду через `POST /api/command`.
8. Проверить `ws://192.168.4.1/ws` из web-клиента или тестового инструмента.

## Что именно нужно увидеть

### Проверка Wi‑Fi endpoint

Ожидаемые признаки:

- `/api/wifi` отвечает валидным JSON;
- поле `initialized` равно `true`;
- поле `apStarted` равно `true`;
- `apSsid` начинается с `JC-ESP32P4M3`;
- `apIp` обычно равно `192.168.4.1` или уже содержит это значение в ответе.

### Проверка общей телеметрии

Ожидаемые признаки:

- `/api/telemetry` отвечает JSON без HTTP-ошибки;
- в ответе есть блоки `system`, `stepper`, `wifi`;
- при подключенном MPU также заполнен блок `mpu`.

### Проверка управления двигателем

Ожидаемые признаки:

- команда `s` переводит `stepper.mode` в `stop`;
- команда `w` переводит `stepper.mode` в `sweep`;
- команда `f` переводит в `forward`;
- возвращаемый после команды JSON отражает новое состояние.

### Проверка WebSocket

Ожидаемые признаки:

- соединение с `/ws` успешно устанавливается;
- клиент получает JSON примерно раз в секунду;
- отправка символа-команды через WS приводит к изменению состояния stepper;
- следующий push уже содержит обновленное состояние.

## Почему этот сценарий важен

Он подтверждает не только работу Wi‑Fi, но и весь сетевой слой проекта целиком:

- SoftAP поднимается;
- IP-доступ работает;
- HTTP server поднят;
- JSON-телеметрия собирается корректно;
- команды доходят до исполнительной логики;
- WebSocket-пуш функционирует.

## Что этот сценарий не покрывает

Проверка без UART не заменяет полностью низкоуровневую диагностику. Она не показывает напрямую:

- ранние boot-логи;
- подробные ошибки I2C;
- текстовую MPU pretty-строку;
- сообщения об инициализации драйверов.

Но именно поэтому она и ценна: если сетевой сценарий проходит, значит проект уже полезен как самостоятельное устройство, а не только как объект для serial-отладки.

## Короткий practical checklist

- [ ] SoftAP виден
- [ ] подключение к AP успешно
- [ ] `/api/wifi` отвечает
- [ ] `/api/telemetry` отвечает
- [ ] `POST /api/command` меняет состояние
- [ ] `/ws` получает push-обновления

Этот checklist можно почти напрямую переносить в раздел методики испытаний для курсовой.



---

## [120] 07-glossary/Glossary.md

# Glossary

AP: Access Point, режим точки доступа. ESP создает Wi-Fi сеть.

STA: Station, режим клиента. ESP подключается к Wi-Fi сети роутера.

APSTA: комбинированный режим, где AP и STA работают вместе.

GPIO: general purpose input/output pin.

I2C: двухпроводная шина для датчиков и периферии.

SDA: линия данных I2C.

SCL: линия такта I2C.

L293D: драйвер двигателя, принимает логические уровни от ESP и управляет обмотками.

MPU9250: IMU-сенсор с акселерометром, гироскопом и магнитометром.

WHO_AM_I: регистр идентификации MPU.

HTTP endpoint: URL, который обрабатывает HTTP server.

WebSocket: постоянное соединение для двусторонних сообщений.

NVS: non-volatile storage во flash.

Kconfig: описание настраиваемых опций ESP-IDF.

sdkconfig: выбранные значения опций сборки.



---

## [121] 08-course-paper/Current limitations.md

# Current limitations

Эта страница фиксирует не недостатки «вообще», а именно текущие ограничения реализованной версии проекта. Для курсовой такой раздел важен: он показывает, что автор понимает границы применимости системы и отличает рабочий прототип от завершенного промышленного решения.

## 1. Проект ориентирован на лабораторный стенд, а не на промышленный deployment

Текущая версия хорошо подходит для демонстрации архитектуры, взаимодействия модулей и удаленного управления, но не претендует на промышленную степень завершенности. В частности, в проекте нет полноценного слоя production-grade fault handling, обновления прошивки, персистентной конфигурации и расширенной security-модели.

## 2. Сетевой профиль в основном AP-first

По умолчанию система поднимает собственную точку доступа и не подключается к внешнему роутеру. Это удобно для автономной демонстрации, но ограничивает сценарии, где устройство должно быть частью уже существующей инфраструктуры.

## 3. Сетевая безопасность упрощена

Пароль SoftAP и прочие параметры заданы как часть конфигурации лабораторного стенда. Для учебного проекта это приемлемо, но для серьезного внедрения потребовались бы:

- более строгая политика хранения/смены учетных данных;
- более сильные требования к API security;
- ограничение открытого управления исполнительными механизмами по сети.

## 4. Работа с MPU реализована в базовом режиме

Проект решает задачу обнаружения устройства и чтения ключевых данных, но не реализует полноценную высокоуровневую обработку инерциальной информации. Сейчас отсутствуют, например:

- калибровка сенсора;
- фильтрация шумов;
- fusion-алгоритмы ориентации;
- долговременная компенсация дрейфа.

То есть датчик уже полезен как источник телеметрии, но не как законченная навигационная подсистема.

## 5. Управление шаговым двигателем остается демонстрационным

Step-by-step управление, sweep-режим и изменение скорости уже реализованы, однако в текущем проекте нет:

- сложного профилирования движения;
- контроля ускорения/торможения;
- обратной связи по положению;
- защиты от механических предельных состояний через концевики.

Следовательно, модуль подходит для демонстрации управления, но не является завершенной системой позиционирования.

## 6. Архитектура deliberately simple, но не максимально масштабируемая

Единый `app_tick()` отлично подходит для понимания системы и лабораторной разработки. Однако при резком росте числа подсистем или требований по real-time поведению может потребоваться переход к более сложной многозадачной модели.

## 7. Некоторые возможности существуют как задел, но не как полностью развернутый runtime-сценарий

В коде уже есть foundation для расширения поведения, однако не все потенциальные возможности включены в основной пользовательский сценарий. Это нормальное состояние исследовательского прототипа, но важно явно это признавать в документации.

## 8. Документация и API ориентированы на разработчика, а не на конечного пользователя

Текущая документация уже стала насыщенной и структурной, но она все еще инженерная по характеру. Для реального конечного пользователя потребовались бы отдельные инструкции, UI-гайды и, возможно, более строгая спецификация API.

## Вывод

Ограничения проекта не обесценивают его, а задают честные рамки: сейчас это сильный лабораторный embedded-прототип с хорошей модульной архитектурой, сетевой наблюдаемостью и несколькими реальными подсистемами, но без претензии на завершенный промышленный продукт.


---

## [122] 08-course-paper/Engineering decisions.md

# Engineering decisions

На этой странице собраны ключевые инженерные решения проекта и причины, по которым текущая архитектура устроена именно так.

## 1. Тонкий `main` и orchestration через `app`

В проекте `main/main.c` почти пустой: он логирует старт, вызывает `app_init()` и затем регулярно вызывает `app_tick()`.

Это решение полезно по нескольким причинам:

- точка входа остается простой и понятной;
- прикладная логика не размазывается по `main`;
- архитектуру легче расширять и документировать;
- тестирование и анализ удобнее проводить через один orchestration-слой.

По сути `components/app/src/app.c` выступает как системный координатор, а не как еще один произвольный модуль.

## 2. Модульное разделение по ответственности

Проект разделен на отдельные компоненты:

- Wi‑Fi;
- network API;
- stepper;
- pretty telemetry для MPU;
- I2C bus;
- минимальный MPU helper.

Такое разделение уменьшает связанность и облегчает локальную доработку. Например, можно менять формат JSON в `app_net.c`, не переписывая код I2C-доступа.

## 3. Единый кооперативный `app_tick()` вместо набора отдельных задач

Хотя проект работает поверх `FreeRTOS`, прикладной уровень не разбит на большое количество независимых задач. Вместо этого используется единый периодический tick.

Преимущества такого решения:

- проще reasoning по поведению системы;
- меньше конкурирующих контекстов исполнения;
- меньше риска гонок и сложных межзадачных ошибок;
- удобнее лабораторная отладка.

Для прототипа и учебной работы это более прозрачная модель, чем избыточная многозадачность.

## 4. Разделение transport layer и application layer в сети

Подъем Wi‑Fi вынесен в `app_wifi.c`, а HTTP/WebSocket API — в `app_net.c`. Это значит, что транспорт и прикладной протокол не смешиваются.

Такое решение позволяет:

- отдельно диагностировать проблемы радиосети и проблемы API;
- включать/выключать сетевые возможности на уровне архитектуры;
- документировать сетевую часть как двухслойную систему: сеть плюс сервисы поверх сети.

## 5. SoftAP-first профиль

Текущая конфигурация ориентирована на SoftAP как основной режим доступа. Это сделано потому, что для лабораторного стенда важно быть автономным и не зависеть от внешнего роутера.

Преимущества:

- устройство можно демонстрировать в любом помещении;
- меньше внешних зависимостей;
- проще воспроизводимость экспериментов;
- легче проверять HTTP/WebSocket API без дополнительной инфраструктуры.

## 6. Единое командное ядро для UART и сети

Управление шаговым двигателем построено так, что разные интерфейсы ввода сходятся в общий механизм интерпретации команд. Это одно из наиболее удачных решений проекта.

Преимущества:

- одинаковое поведение команд при локальном и удаленном управлении;
- меньше дублирования логики;
- проще поддержка и документация;
- удобнее развитие внешнего UI.

## 7. Snapshot/status API вместо доступа к внутренним переменным

Сетевой слой не читает внутренние глобальные переменные других модулей напрямую. Вместо этого используются функции вроде `app_wifi_get_status()` и `app_stepper_get_snapshot()`.

Это повышает качество архитектуры, потому что:

- состояния формализованы;
- модуль сам контролирует, что и как он экспортирует наружу;
- уменьшается жесткая связанность;
- JSON-слой опирается на стабильные интерфейсы, а не на детали реализации.

## 8. Диагностика как часть штатного сценария запуска

I2C scan, WHO_AM_I probe, сетевые статусы и текстовая телеметрия встроены в нормальный runtime, а не оставлены только как внешние debug-утилиты.

Это важное решение для лабораторного проекта: система должна уметь сама объяснять, что с ней происходит, а не только работать в идеальном случае.

## 9. Не считать отказ UART фатальным для stepper-модуля

Если инициализация UART не удалась, stepper-логика остается доступной через другие механизмы. Это повышает устойчивость системы к частичным отказам и показывает правильный инженерный подход: потеря одного интерфейса не должна автоматически уничтожать всю функциональность исполнительного узла.

## Вывод

Текущая архитектура проекта не случайна. Она построена вокруг нескольких осознанных принципов: модульность, наблюдаемость, автономность стенда, единый цикл управления и единые интерфейсы состояния/команд. Именно эти решения делают проект удобным не только для запуска, но и для инженерного анализа и последующего развития.


---

## [123] 08-course-paper/Future development.md

# Future development

Эта страница описывает наиболее логичные направления развития проекта. Для курсовой это важный раздел, потому что он показывает не только текущее состояние прототипа, но и траекторию его инженерного роста.

## 1. Развитие сетевого интерфейса

Текущий REST/WebSocket API уже позволяет получать телеметрию и отправлять команды, но его можно развивать дальше:

- расширить набор endpoint'ов;
- ввести более формальную схему JSON-ответов;
- добавить явную версионизацию API;
- реализовать более удобный web-интерфейс поверх существующего канала.

Это превратит сеть из вспомогательного диагностического слоя в полноценный пользовательский интерфейс системы.

## 2. Переход от базовой телеметрии MPU к более интеллектуальной обработке

Перспективное направление — развитие sensor pipeline:

- калибровка акселерометра и гироскопа;
- цифровая фильтрация измерений;
- вычисление углов ориентации;
- оценка динамики движения на основе более устойчивых алгоритмов.

Тогда проект сможет демонстрировать не только чтение данных сенсора, но и их инженерную интерпретацию на более высоком уровне.

## 3. Усложнение stepper-подсистемы

Для шагового двигателя можно добавить:

- профили разгона и торможения;
- более точное управление скоростью;
- сценарии позиционирования;
- поддержку датчиков обратной связи или концевых выключателей;
- защиту от некорректных режимов работы.

Это переведет исполнительный модуль из демонстрационного в более прикладной.

## 4. Улучшение fault handling и самодиагностики

Сейчас система уже хорошо сообщает о проблемах в логах и статусах. Следующий шаг — сделать диагностику еще более формальной:

- ввести классификацию ошибок;
- различать recoverable и fatal состояния;
- расширить machine-readable telemetry по ошибкам;
- добавить автоматические сценарии восстановления там, где это безопасно.

## 5. Развитие конфигурирования

Сейчас проект хорошо конфигурируется через `Kconfig`, но можно пойти дальше:

- добавить runtime-параметры для части настроек;
- хранить пользовательские сетевые параметры в энергонезависимой памяти;
- отделить developer defaults от deployment-конфигурации.

Это сделает систему гибче без потери прозрачности.

## 6. Развитие многокомпонентного сценария

Сейчас проект уже объединяет датчик, двигатель, Wi‑Fi и API. Следующий шаг — усилить связи между ними на прикладном уровне. Например:

- использовать данные MPU для реакции системы управления;
- связывать режим stepper с внешними событиями сети;
- строить более сложные сценарии работы на основе состояния нескольких подсистем сразу.

## 7. Повышение качества пользовательского уровня

Для завершенного стенда полезно развивать не только прошивку, но и user-facing слой:

- web dashboard;
- наглядные графики телеметрии;
- журнал событий;
- быстрые кнопки команд управления;
- сценарии демонстрации для защиты/лабораторной работы.

## Вывод

Наиболее сильная сторона проекта в том, что он уже имеет хорошую архитектурную основу для роста. Здесь не нужно «переписывать всё с нуля» — можно последовательно усиливать отдельные подсистемы: телеметрию, управление, диагностику, API и пользовательский интерфейс. Это делает проект хорошей базой как для курсовой, так и для дальнейших экспериментальных доработок.


---

## [124] 08-course-paper/README.md

# Материалы для курсовой

Этот раздел предназначен не для низкоуровневой навигации по исходникам, а для подготовки связного инженерного текста по проекту. Здесь собраны страницы, которые можно почти напрямую использовать как основу для введения, аналитической части, архитектурной главы и заключения курсовой работы.

## Для чего нужен этот раздел

В остальной документации акцент сделан на точном описании исходников: кто кого вызывает, где лежит компонент, какие структуры формируют JSON, как устроен tick-loop. Для курсовой этого недостаточно. Нужен еще один слой — смысловой:

- какие технологии применены;
- почему архитектура выбрана именно такой;
- какие инженерные компромиссы уже есть в текущей версии;
- какие ограничения имеет прототип;
- как проект можно развивать дальше.

Именно этот слой и собран здесь.

## Состав раздела

- [[08-course-paper/Technologies and stack]]
- [[08-course-paper/Engineering decisions]]
- [[08-course-paper/Current limitations]]
- [[08-course-paper/Future development]]

## Как использовать при написании курсовой

Практический маршрут обычно такой:

1. Из `00-index` и `02-architecture` взять фактическую структуру системы.
2. Из `03-components` и `04-functions` взять точные технические детали.
3. Из этого раздела взять связующие объяснения: зачем используются конкретные технологии, почему модули разделены именно так, какие решения уже приняты и какие ограничения остаются.

Тогда итоговый текст будет не пересказом кода, а инженерным описанием проекта.

## На какие разделы опирается этот материал

- [[02-architecture/System overview]]
- [[02-architecture/Boot and main loop]]
- [[02-architecture/WiFi HTTP WebSocket architecture]]
- [[03-components/app component]]
- [[05-config/Configuration overview]]
- [[06-operations/Build and verification]]


---

## [125] 08-course-paper/Technologies and stack.md

# Technologies and stack

Эта страница фиксирует технологический стек проекта `p4_lab` и объясняет, какую задачу решает каждый выбранный уровень.

## Аппаратная платформа

Базовая аппаратная платформа — `ESP32-P4`. Проект строится как лабораторная embedded-прошивка, которая объединяет несколько типовых для встраиваемых систем задач:

- работа с цифровыми выводами и периферией;
- обмен по I2C;
- опрос инерциального датчика;
- управление исполнительным механизмом;
- беспроводной доступ к телеметрии и управлению.

В качестве датчика используется устройство семейства `MPU-9250`, а в качестве силового интерфейса двигателя — `L293D`.

## Программная платформа

Основной программный стек — `ESP-IDF`. Он дает проекту:

- модель сборки через `CMake` и `idf.py`;
- системные библиотеки и драйверы;
- поддержку `FreeRTOS`;
- сетевой стек и HTTP server;
- механизмы конфигурирования через `Kconfig`/`sdkconfig`.

Выбор ESP-IDF логичен, потому что проект ориентирован не на абстрактный микроконтроллерный код, а на реальное приложение под экосистему Espressif.

## Язык и модель реализации

Основной язык проекта — `C`. Это типичный выбор для embedded-прошивки, где важны:

- прямой контроль над памятью и периферией;
- предсказуемость исполнения;
- простая интеграция с SDK уровня ESP-IDF;
- минимальные накладные расходы.

При этом архитектура проекта старается оставаться не «монолитным С-кодом», а модульной системой с явными границами между подсистемами.

## RTOS и модель выполнения

Проект использует `FreeRTOS`, но не строит сложную многозадачную структуру из множества конкурентных задач. Основная логика организована через:

- `app_main()`;
- `app_init()`;
- периодический `app_tick()`.

Это означает, что система использует RTOS как базовую исполнительную среду, но прикладная логика реализована через кооперативный управляющий цикл. Такой подход уменьшает сложность и упрощает анализ поведения прототипа.

## Сетевой стек и API

Сетевой уровень включает:

- Wi‑Fi bringup;
- режим SoftAP по умолчанию;
- опциональный AP+STA режим;
- `esp_http_server` для REST API;
- WebSocket для push-телеметрии.

Это делает устройство не просто локальным контроллером, а сетевым embedded-узлом с удаленным доступом к состоянию и командам.

## Подсистема датчика

Для работы с MPU используются два уровня:

1. `i2c_bus` — общий слой шины, инициализации, scan, read/write.
2. `mpu9250` + `app_mpu_pretty` — минимальная идентификация датчика и прикладное чтение телеметрии.

Такое разделение позволяет не смешивать транспортный доступ к шине с логикой интерпретации измерений.

## Подсистема исполнительного механизма

Управление шаговым двигателем вынесено в отдельный модуль `app_stepper`. Он объединяет:

- управление фазами через GPIO;
- работу с драйвером `L293D`;
- символьный протокол команд;
- локальный UART-ввод;
- сетевой путь управления;
- snapshot-модель состояния.

Таким образом исполнительный механизм рассматривается как самостоятельная подсистема с единым command core.

## Конфигурирование

Проект конфигурируется через:

- `Kconfig`;
- `sdkconfig`;
- `sdkconfig.defaults`.

Это позволяет задавать режимы работы, распиновку, сетевые параметры и опции включения модулей без прямого редактирования исходников.

## Телеметрия и диагностика

В системе используются несколько форм наблюдаемости:

- обычные текстовые логи;
- строки `@telemetry` для машинного парсинга;
- JSON-ответы HTTP API;
- WebSocket push-обновления.

Это повышает удобство отладки и делает проект пригодным как для ручной проверки, так и для интеграции с внешним UI.

## Вывод

Технологический стек проекта подобран так, чтобы одна прошивка демонстрировала полный путь от низкоуровневого доступа к датчику и управлению двигателем до беспроводного сетевого API и удаленной телеметрии. Для учебно-исследовательской работы это сильная комбинация, потому что она показывает сразу несколько классов задач embedded-разработки в одной связной системе.
