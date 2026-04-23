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

