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

