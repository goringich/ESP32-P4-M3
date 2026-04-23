# App Kconfig

Файл: `components/app/Kconfig`.

Главные группы:

- app mode;
- tick logging;
- Wi-Fi bringup;
- Wi-Fi AP settings;
- Wi-Fi STA settings;
- HTTP/WebSocket enable;
- L293D stepper settings.

`APP_MODE` сейчас выбирает один из режимов:

- `APP_MODE_MPU9250`;
- `APP_MODE_L293D_TEST`.

Wi-Fi options:

- `APP_WIFI_SMOKE`: включает Wi-Fi bringup на boot.
- `APP_WIFI_AP_SSID_PREFIX`: префикс SoftAP SSID.
- `APP_WIFI_AP_PASSWORD`: пароль SoftAP.
- `APP_WIFI_AP_CHANNEL`: канал SoftAP.
- `APP_WIFI_SCAN_MAX_AP`: максимум AP records при scan.
- `APP_WIFI_CONNECT`: включает попытку подключения к роутеру.
- `APP_WIFI_SSID`: SSID роутера.
- `APP_WIFI_PASSWORD`: пароль роутера.
- `APP_NET_ENABLE`: включает HTTP/WebSocket API.

Stepper options:

- `APP_L293D_IN1_GPIO`
- `APP_L293D_IN2_GPIO`
- `APP_L293D_IN3_GPIO`
- `APP_L293D_IN4_GPIO`
- `APP_L293D_STEP_DELAY_MS`
- `APP_STEPPER_UART_BAUD_RATE`
- `APP_STEPPER_LED_ENABLE`
- `APP_STEPPER_LED_GPIO`

