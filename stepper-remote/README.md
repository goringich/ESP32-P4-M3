# Stepper Remote

This web stack is the operator UI for the ESP32-P4 gyroscope platform bench in this repo.

## What works

- Local web UI: served from the backend on `http://127.0.0.1:3001/`
- Serial workflow: browser -> local backend -> `/dev/ttyUSB0`
- Wi-Fi workflow: browser -> local backend -> ESP AP at `http://192.168.4.1`
- BLE status is exposed by firmware telemetry and shown in the UI

## One-command start

From the repo root:

```bash
./scripts/run_stepper_remote_web.sh
```

The script:

1. builds the frontend
2. builds the backend
3. starts the backend that serves the built frontend

Then open:

- `http://127.0.0.1:3001/` for the main UI
- `http://127.0.0.1:3001/pad` for the simple pad view

## Important transport note

Opening the web UI locally and controlling the board over Wi-Fi are different things.

- The local UI can open as long as the backend is running.
- Wi-Fi transport from this PC to the ESP AP requires a real Wi-Fi adapter on the host.
- On this machine, recent checks showed `WIFI-HW missing`, so `http://192.168.4.1` is not reachable from this PC until Wi-Fi hardware is available.

Because of that:

- use `serial` mode from this workstation when working directly over USB
- use another phone/laptop with Wi-Fi if you want to drive the ESP AP over `wifi` mode

## Backend ports

- backend API + static UI: `3001`
- frontend dev server, if you run it separately: Vite with `/api` proxy to `3001`

## Main API surfaces

- `GET /api/ports`
- `POST /api/connect`
- `POST /api/disconnect`
- `POST /api/command`
- `GET /api/telemetry`
- `GET /api/logs`
- `GET /api/logs/stream`
- `POST /api/transport`
- `POST /api/tooling/build`
- `POST /api/tooling/flash`
