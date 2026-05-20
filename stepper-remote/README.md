# Stepper Remote

This web stack is the operator UI for the ESP32-P4 gyroscope platform bench in this repo.

## What works

- Local web UI: served from the backend on `http://127.0.0.1:3001/`
- Serial workflow: browser -> local backend -> `/dev/ttyUSB0`
- Wi-Fi workflow: browser -> backend proxy -> ESP AP at `http://192.168.4.1`
- BLE status is exposed by firmware telemetry and shown in the UI

## One-command start

From the repo root:

```bash
./scripts/run_stepper_remote_web.sh
```

The script:

1. builds the frontend
2. builds the backend
3. starts the backend that serves the built frontend on `0.0.0.0:3001`

Then open:

- `http://127.0.0.1:3001/` for the main UI
- `http://127.0.0.1:3001/pad` for the simple pad view
- `http://<backend-host-ip>:3001/` from another device that can reach the backend host

## Important transport note

Opening the web UI locally and controlling the board over Wi-Fi are different things.

- The local UI can open as long as the backend is running.
- In `wifi` mode the browser talks only to the backend. The backend proxies requests to the ESP AP.
- Because of that, the browser device may stay on another Wi-Fi network if it can reach the backend host.
- But the backend host itself still must have a real route to the ESP AP: second adapter, dual-homed host, or router route.
- Wi-Fi transport from this PC to the ESP AP requires a real Wi-Fi adapter on the host.
- On this machine, recent checks showed `WIFI-HW missing`, so `http://192.168.4.1` is not reachable from this PC until Wi-Fi hardware is available.

Because of that:

- use `serial` mode from this workstation when working directly over USB
- use another phone/laptop with Wi-Fi if you want to drive the ESP AP over `wifi` mode
- or run the backend on a machine that can both reach `192.168.4.1` and expose `http://<backend-ip>:3001` to the browser device

## ESP AP credentials

- SSID prefix: `JC-ESP32P4M3`
- Password: `00000000`

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
