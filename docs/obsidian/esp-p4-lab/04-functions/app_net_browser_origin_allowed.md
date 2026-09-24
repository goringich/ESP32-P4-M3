# app_net_browser_origin_allowed

Исходник: `components/app/src/app_net.c`.

Проверяет browser `Origin` относительно HTTP `Host`.

- если `Origin` отсутствует, запрос рассматривается как non-browser/server-to-server и допускается;
- если `Origin` присутствует, ожидается ровно `http://<Host>`;
- слишком длинные/нечитаемые headers отклоняются fail-closed.

Проверка применяется к HTTP command endpoint и WebSocket browser handshake.

Это защита от ненужного cross-origin browser control. Она не является полноценной authentication и не заменяет trusted network.
