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

