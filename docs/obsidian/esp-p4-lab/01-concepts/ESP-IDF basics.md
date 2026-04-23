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

