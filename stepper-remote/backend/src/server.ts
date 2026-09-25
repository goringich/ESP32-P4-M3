import express from 'express';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { WifiBridgeManager } from './remote/wifi-bridge.js';
import { SerialManager } from './serial/serial-manager.js';
import { applyToolingTelemetry } from './telemetry/telemetry-parser.js';
import { ToolingManager } from './tooling/tooling-manager.js';
import type {
  SerialConnectionState,
  SerialLogEntry,
  TelemetryState,
  TransportState,
  ToolingState,
} from './types/serial.js';
import type {
  FlashPayload,
  OpenPortPayload,
  SendCommandPayload,
} from './types/serial.js';

type SerialApi = {
  listPorts: () => Promise<unknown[]>;
  getState: () => SerialConnectionState;
  open: (payload: OpenPortPayload) => Promise<void>;
  close: () => Promise<void>;
  send: (command: string) => Promise<void>;
  pushSystemLog: (line: string) => void;
  getLogs: () => SerialLogEntry[];
  getTelemetry: () => TelemetryState;
  onLog: (listener: (entry: SerialLogEntry) => void) => () => void;
  onState: (listener: (state: SerialConnectionState) => void) => () => void;
  onTelemetry: (listener: (state: TelemetryState) => void) => () => void;
};

type ToolingApi = {
  getState: () => ToolingState;
  startBuild: () => void;
  startFlash: (portPath: string) => void;
  onState: (listener: (state: ToolingState) => void) => () => void;
};

type TransportApi = {
  getState: () => TransportState;
  getTelemetry: () => TelemetryState;
  configure: (next: {
    mode?: 'serial' | 'wifi';
    wifiBaseUrl?: string;
  }) => Promise<TransportState>;
  sendCommand: (command: string) => Promise<void>;
  onState: (listener: (state: TransportState) => void) => () => void;
  onTelemetry: (listener: (state: TelemetryState) => void) => () => void;
};

type AppDependencies = {
  serial?: SerialApi;
  tooling?: ToolingApi;
  transport?: TransportApi;
};

type PendingReconnect = {
  path: string;
  baudRate: number;
};

export function isLoopbackHostname(hostname: string) {
  const normalized = hostname.trim().toLowerCase();
  return normalized === 'localhost'
    || normalized === '127.0.0.1'
    || normalized === '::1'
    || normalized === '[::1]';
}

export function browserOriginAllowed(origin: string, requestHost: string | undefined) {
  try {
    const url = new URL(origin);
    if (isLoopbackHostname(url.hostname)) {
      return true;
    }

    const allowedOrigin = process.env.STEPPER_REMOTE_ALLOWED_ORIGIN?.trim();
    if (allowedOrigin) {
      return origin === allowedOrigin;
    }

    return process.env.STEPPER_REMOTE_ALLOW_REMOTE === '1'
      && Boolean(requestHost)
      && url.host === requestHost;
  } catch {
    return false;
  }
}

export function createApp(deps: AppDependencies = {}) {
  const app = express();
  const serial = deps.serial ?? new SerialManager();
  const tooling = deps.tooling ?? new ToolingManager((line) => serial.pushSystemLog(line));
  const transport = deps.transport ?? new WifiBridgeManager((line) => serial.pushSystemLog(line));
  const frontendDistDir = path.resolve(
    path.dirname(fileURLToPath(import.meta.url)),
    '../../frontend/dist'
  );
  const getTransportState = () => transport.getState();
  const shouldUseWifiTelemetry = () => {
    const state = getTransportState();
    return state.mode === 'wifi' && state.wifiConnected;
  };
  const getTelemetry = () =>
    applyToolingTelemetry(
      shouldUseWifiTelemetry() ? transport.getTelemetry() : serial.getTelemetry(),
      tooling.getState()
    );
  let pendingReconnect: PendingReconnect | null = null;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  tooling.onState((state) => {
    if (state.isRunning) {
      return;
    }

    if (!pendingReconnect || state.lastAction !== 'flash') {
      return;
    }

    const reconnect = pendingReconnect;
    pendingReconnect = null;

    if (state.lastExitCode !== 0) {
      serial.pushSystemLog('[tool] flash finished, serial auto-reconnect skipped because flashing failed');
      return;
    }

    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
    }

    serial.pushSystemLog(
      `[tool] flash finished, waiting for board reboot before reconnecting ${reconnect.path} @ ${reconnect.baudRate}`
    );

    reconnectTimer = setTimeout(() => {
      serial
        .open({
          path: reconnect.path,
          baudRate: reconnect.baudRate,
        })
        .then(() => {
          serial.pushSystemLog(`[tool] serial auto-reconnect requested for ${reconnect.path}`);
        })
        .catch((error) => {
          serial.pushSystemLog(
            `[tool] serial auto-reconnect failed: ${
              error instanceof Error ? error.message : 'unknown error'
            }`
          );
        })
        .finally(() => {
          reconnectTimer = null;
        });
    }, 1200);
  });

  app.use((req, res, next) => {
    const remoteEnabled = process.env.STEPPER_REMOTE_ALLOW_REMOTE === '1';
    if (!remoteEnabled && !isLoopbackHostname(req.hostname)) {
      res.status(403).json({
        ok: false,
        error: 'remote host access is disabled',
      });
      return;
    }

    const origin = req.get('origin');
    const mutating = !['GET', 'HEAD', 'OPTIONS'].includes(req.method);
    if (mutating && origin && !browserOriginAllowed(origin, req.get('host'))) {
      res.status(403).json({
        ok: false,
        error: 'browser origin is not allowed',
      });
      return;
    }

    next();
  });
  app.use(express.json());

  app.get('/api/transport', (_req, res) => {
    res.json({
      ok: true,
      transport: getTransportState(),
    });
  });

  app.post('/api/transport', async (req, res) => {
    try {
      const nextState = await transport.configure({
        mode: req.body?.mode,
        wifiBaseUrl: req.body?.wifiBaseUrl,
      });
      res.json({
        ok: true,
        transport: nextState,
      });
    } catch (error) {
      res.status(500).json({
        ok: false,
        error: error instanceof Error ? error.message : 'unknown error',
      });
    }
  });

  app.get('/api/ports', async (_req, res) => {
    try {
      const ports = await serial.listPorts();
      res.json({ ok: true, ports });
    } catch (error) {
      res.status(500).json({
        ok: false,
        error: error instanceof Error ? error.message : 'unknown error',
      });
    }
  });

  app.get('/api/connection', (_req, res) => {
    res.json({
      ok: true,
      connection: serial.getState(),
    });
  });

  app.get('/api/tooling', (_req, res) => {
    res.json({
      ok: true,
      tooling: tooling.getState(),
    });
  });

  app.get('/api/telemetry', (_req, res) => {
    res.json({
      ok: true,
      telemetry: getTelemetry(),
    });
  });

  app.post('/api/connect', async (req, res) => {
    try {
      const body = req.body as OpenPortPayload;
      await serial.open(body);

      res.json({
        ok: true,
        connection: serial.getState(),
      });
    } catch (error) {
      res.status(500).json({
        ok: false,
        error: error instanceof Error ? error.message : 'unknown error',
      });
    }
  });

  app.post('/api/disconnect', async (_req, res) => {
    try {
      await serial.close();

      res.json({
        ok: true,
        connection: serial.getState(),
      });
    } catch (error) {
      res.status(500).json({
        ok: false,
        error: error instanceof Error ? error.message : 'unknown error',
      });
    }
  });

  app.post('/api/command', async (req, res) => {
    try {
      const body = req.body as SendCommandPayload;
      const transportState = getTransportState();

      if (transportState.mode === 'wifi') {
        try {
          await transport.sendCommand(body.command);
        } catch (error) {
          if (!serial.getState().isOpen) {
            throw error;
          }

          serial.pushSystemLog(
            `[wifi] command fallback to UART because Wi-Fi send failed: ${
              error instanceof Error ? error.message : 'unknown error'
            }`
          );
          await serial.send(body.command);
        }
      } else {
        await serial.send(body.command);
      }

      res.json({
        ok: true,
      });
    } catch (error) {
      res.status(500).json({
        ok: false,
        error: error instanceof Error ? error.message : 'unknown error',
      });
    }
  });

  app.post('/api/tooling/build', (_req, res) => {
    try {
      tooling.startBuild();
      res.json({
        ok: true,
        tooling: tooling.getState(),
      });
    } catch (error) {
      res.status(409).json({
        ok: false,
        error: error instanceof Error ? error.message : 'unknown error',
      });
    }
  });

  app.post('/api/tooling/flash', async (req, res) => {
    try {
      const body = req.body as FlashPayload;
      const currentConnection = serial.getState();
      const reconnectPath = body.portPath.trim();
      const reconnectBaudRate = currentConnection.baudRate ?? 115200;

      pendingReconnect = {
        path: reconnectPath,
        baudRate: reconnectBaudRate,
      };

      await serial.close();
      tooling.startFlash(reconnectPath);
      res.json({
        ok: true,
        tooling: tooling.getState(),
        connection: serial.getState(),
      });
    } catch (error) {
      pendingReconnect = null;
      res.status(409).json({
        ok: false,
        error: error instanceof Error ? error.message : 'unknown error',
      });
    }
  });

  app.post('/api/debug/log', (req, res) => {
    const message =
      typeof req.body?.message === 'string' && req.body.message.trim()
        ? req.body.message.trim()
        : `[ui] test console line @ ${new Date().toLocaleTimeString()}`;

    serial.pushSystemLog(message);

    res.json({
      ok: true,
      message,
    });
  });

  app.get('/api/logs', (_req, res) => {
    res.json({
      ok: true,
      logs: serial.getLogs(),
    });
  });

  app.get('/api/logs/stream', (req, res) => {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('X-Accel-Buffering', 'no');
    res.flushHeaders();

    res.write(`event: state\n`);
    res.write(`data: ${JSON.stringify(serial.getState())}\n\n`);

    res.write(`event: tooling\n`);
    res.write(`data: ${JSON.stringify(tooling.getState())}\n\n`);

    res.write(`event: transport\n`);
    res.write(`data: ${JSON.stringify(getTransportState())}\n\n`);

    res.write(`event: telemetry\n`);
    res.write(`data: ${JSON.stringify(getTelemetry())}\n\n`);

    for (const entry of serial.getLogs()) {
      res.write(`event: log\n`);
      res.write(`data: ${JSON.stringify(entry)}\n\n`);
    }

    const heartbeat = setInterval(() => {
      res.write(`: ping ${Date.now()}\n\n`);
    }, 15000);

    const unsubscribeLog = serial.onLog((entry) => {
      res.write(`event: log\n`);
      res.write(`data: ${JSON.stringify(entry)}\n\n`);
    });

    const unsubscribeState = serial.onState((state) => {
      res.write(`event: state\n`);
      res.write(`data: ${JSON.stringify(state)}\n\n`);
    });

    const unsubscribeTooling = tooling.onState((state) => {
      res.write(`event: tooling\n`);
      res.write(`data: ${JSON.stringify(state)}\n\n`);

      res.write(`event: telemetry\n`);
      res.write(`data: ${JSON.stringify(getTelemetry())}\n\n`);
    });

    const unsubscribeTelemetry = serial.onTelemetry((state) => {
      if (shouldUseWifiTelemetry()) {
        return;
      }
      res.write(`event: telemetry\n`);
      res.write(`data: ${JSON.stringify(applyToolingTelemetry(state, tooling.getState()))}\n\n`);
    });

    const unsubscribeTransport = transport.onState((state) => {
      res.write(`event: transport\n`);
      res.write(`data: ${JSON.stringify(state)}\n\n`);

      res.write(`event: telemetry\n`);
      res.write(`data: ${JSON.stringify(getTelemetry())}\n\n`);
    });

    const unsubscribeTransportTelemetry = transport.onTelemetry((state) => {
      if (!shouldUseWifiTelemetry()) {
        return;
      }
      res.write(`event: telemetry\n`);
      res.write(`data: ${JSON.stringify(applyToolingTelemetry(state, tooling.getState()))}\n\n`);
    });

    req.on('close', () => {
      clearInterval(heartbeat);
      unsubscribeLog();
      unsubscribeState();
      unsubscribeTooling();
      unsubscribeTelemetry();
      unsubscribeTransport();
      unsubscribeTransportTelemetry();
      res.end();
    });
  });

  app.use(express.static(frontendDistDir));
  app.get('/pad', (_req, res) => {
    res.sendFile(path.join(frontendDistDir, 'pad.html'));
  });
  app.get(/^(?!\/api).*/, (_req, res) => {
    res.sendFile(path.join(frontendDistDir, 'index.html'));
  });

  return app;
}

const port = Number.parseInt(process.env.STEPPER_REMOTE_PORT ?? '3001', 10);
const host = process.env.STEPPER_REMOTE_HOST?.trim() || '127.0.0.1';

function collectListenUrls(port: number, bindHost: string) {
  const urls = new Set<string>([`http://127.0.0.1:${port}`]);

  if (isLoopbackHostname(bindHost)) {
    return Array.from(urls);
  }
  let interfaces: ReturnType<typeof os.networkInterfaces>;

  try {
    interfaces = os.networkInterfaces();
  } catch (error) {
    console.warn(
      `networkInterfaces() is unavailable, falling back to localhost only: ${
        error instanceof Error ? error.message : 'unknown error'
      }`
    );
    return Array.from(urls);
  }

  for (const addresses of Object.values(interfaces)) {
    for (const address of addresses ?? []) {
      if (address.internal || address.family !== 'IPv4') {
        continue;
      }
      urls.add(`http://${address.address}:${port}`);
    }
  }

  return Array.from(urls).sort();
}

if (import.meta.url === `file://${process.argv[1]}`) {
  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    throw new Error(`invalid STEPPER_REMOTE_PORT: ${process.env.STEPPER_REMOTE_PORT ?? ''}`);
  }

  const remoteEnabled = process.env.STEPPER_REMOTE_ALLOW_REMOTE === '1';
  if (!isLoopbackHostname(host) && !remoteEnabled) {
    throw new Error(
      'remote bind refused: set STEPPER_REMOTE_ALLOW_REMOTE=1 explicitly'
    );
  }

  const app = createApp();

  app.listen(port, host, () => {
    console.log(`backend listening on ${host}:${port}`);
    for (const url of collectListenUrls(port, host)) {
      console.log(`ui available at ${url}/`);
    }
    if (!isLoopbackHostname(host)) {
      console.warn(
        'remote operator access is enabled; restrict the host firewall and set STEPPER_REMOTE_ALLOWED_ORIGIN'
      );
    }
    console.log('wifi mode is proxied by backend -> ESP AP');
  });
}
