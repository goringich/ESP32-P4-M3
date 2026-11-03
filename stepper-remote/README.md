# Stepper Remote

This web stack is the operator UI for the ESP32-P4 bench infrastructure in this repository.

It can send commands, open serial ports, build firmware, and flash hardware. Treat it as a privileged local operator tool, not as a public web application.

## Safe default

Start from the repository root:

```bash
./scripts/run_stepper_remote_web.sh
```

The backend and Vite tooling bind to loopback by default:

- main UI: `http://127.0.0.1:3001/`
- pad UI: `http://127.0.0.1:3001/pad`

Cross-origin browser access is not enabled by default.

The backend derives the firmware project directory from this repository instead of assuming a machine-specific path. You can still override it with `IDF_PROJECT_DIR`.

## Explicit remote operator mode

LAN exposure is intentionally opt-in because the API can build, flash, connect serial ports, and command the device.

Example:

```bash
STEPPER_REMOTE_HOST=0.0.0.0 \
STEPPER_REMOTE_ALLOW_REMOTE=1 \
STEPPER_REMOTE_ALLOWED_ORIGIN=http://192.168.1.50:3001 \
./scripts/run_stepper_remote_web.sh
```

When remote mode is enabled:

- restrict TCP port 3001 with the host firewall to trusted clients;
- set `STEPPER_REMOTE_ALLOWED_ORIGIN` to the exact browser origin when possible;
- do not expose the service directly to the Internet;
- use a trusted network only.

## Transport model

The operator UI and the ESP transport are separate layers.

- `serial`: browser -> local backend -> serial device;
- `wifi`: browser -> backend -> ESP HTTP API, default ESP base URL `http://192.168.4.1`.

The backend host must have a real route to the ESP Wi-Fi endpoint for Wi-Fi mode to work.

## Environment overrides

- `STEPPER_REMOTE_HOST` — backend/Vite bind host; default `127.0.0.1`;
- `STEPPER_REMOTE_PORT` — backend port; default `3001`;
- `STEPPER_REMOTE_ALLOW_REMOTE=1` — required for non-loopback bind;
- `STEPPER_REMOTE_ALLOWED_ORIGIN` — allowed remote browser origin;
- `IDF_PROJECT_DIR` — firmware project root; defaults to this repository;
- `IDF_PATH` — ESP-IDF root; defaults to `<repo>/esp-idf`;
- `IDF_EXPORT_SCRIPT` — ESP-IDF export script override;
- `ESP_WIFI_BASE_URL` — ESP HTTP base URL; default `http://192.168.4.1`.

## Main API surfaces

Read/status:

- `GET /api/ports`
- `GET /api/connection`
- `GET /api/tooling`
- `GET /api/telemetry`
- `GET /api/logs`
- `GET /api/logs/stream`

Mutating/operator actions:

- `POST /api/connect`
- `POST /api/disconnect`
- `POST /api/command`
- `POST /api/transport`
- `POST /api/tooling/build`
- `POST /api/tooling/flash`

## ESP Wi-Fi defaults

Firmware AP defaults are controlled by `sdkconfig.defaults` and Kconfig. Do not duplicate passwords or private STA credentials in this README.
