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

