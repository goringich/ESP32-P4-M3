import cors from 'cors';
import express from 'express';
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
  const getTelemetry = () =>
    applyToolingTelemetry(
      getTransportState().mode === 'wifi' ? transport.getTelemetry() : serial.getTelemetry(),
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

  app.use(cors());
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
      if (getTransportState().mode === 'wifi') {
        await transport.sendCommand(body.command);
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
      if (getTransportState().mode === 'wifi') {
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
      if (getTransportState().mode !== 'wifi') {
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

const port = 3001;

if (import.meta.url === `file://${process.argv[1]}`) {
  const app = createApp();

  app.listen(port, '0.0.0.0', () => {
    console.log(`backend listening on http://0.0.0.0:${port}`);
  });
}
