import test from 'node:test';
import assert from 'node:assert/strict';
import {
  connectPort,
  createLogsEventSource,
  disconnectPort,
  fetchConnection,
  fetchLogs,
  fetchPorts,
  fetchTelemetry,
  fetchTooling,
  pushDebugLog,
  readJsonOrThrow,
  sendCommand,
  startBuild,
  startFlash,
} from '../src/api/client.ts';

class FakeEventSource {
  url: string;

  constructor(url: string) {
    this.url = url;
  }
}

test('readJsonOrThrow returns parsed payload on ok response', async () => {
  const response = new Response(JSON.stringify({ ok: true, value: 7 }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });

  const result = await readJsonOrThrow<{ value: number }>(response);
  assert.equal(result.value, 7);
});

test('readJsonOrThrow throws API error message on failure response', async () => {
  const response = new Response(JSON.stringify({ ok: false, error: 'boom' }), {
    status: 500,
    headers: { 'Content-Type': 'application/json' },
  });

  await assert.rejects(() => readJsonOrThrow(response), /boom/);
});

test('API client methods call expected endpoints and payloads', async () => {
  const calls: Array<{ input: string; init?: RequestInit }> = [];
  globalThis.fetch = (async (input: string | URL | Request, init?: RequestInit) => {
    const url = typeof input === 'string' ? input : input.toString();
    calls.push({ input: url, init });

    if (url.endsWith('/api/ports')) {
      return new Response(JSON.stringify({ ok: true, ports: [{ path: '/dev/ttyUSB0' }] }));
    }
    if (url.endsWith('/api/connection')) {
      return new Response(JSON.stringify({ ok: true, connection: { isOpen: true, path: '/dev/ttyUSB0', baudRate: 115200 } }));
    }
    if (url.endsWith('/api/logs')) {
      return new Response(JSON.stringify({ ok: true, logs: [{ id: '1', ts: 1, line: 'hello' }] }));
    }
    if (url.endsWith('/api/tooling')) {
      return new Response(JSON.stringify({ ok: true, tooling: { isRunning: false, currentAction: null, lastAction: null, lastExitCode: null, projectDir: '/tmp/project', portPath: null, startedAt: null, finishedAt: null, error: null } }));
    }
    if (url.endsWith('/api/telemetry')) {
      return new Response(JSON.stringify({ ok: true, telemetry: { updatedAt: 1, system: { uptimeMs: 1000, tick: 7, tickDelayMs: 5, firmware: 'hello_world_p4', appMode: 'l293d_test', lastError: null }, mpu: { ready: true, error: null, address: '0x68', whoAmI: '0x71', model: 'MPU9250', uptimeLabel: '00:01', accel: { x: 0.1, y: 0.2, z: 0.3 }, gyro: { x: 1, y: 2, z: 3 }, tempC: 28 }, stepper: { mode: 'forward', sweepState: 'forward', delayMs: 100, stepsPerSecond: 10, phaseIndex: 2, totalSteps: 12, coilsEnabled: true, sweepSteps: 9, uartReady: true, lastCommand: 'f', pins: { in1: 18, in2: 19, in3: 21, in4: 22 }, ledGpio: 2 }, i2c: { ready: true, devices: ['0x68'], detectedMpuAddress: '0x68', lastScanSummary: 'found=1, timeouts=0, other=0', error: null }, wifi: { enabled: true, connected: true, ssid: 'lab', ip: '192.168.0.10', mac: 'AA:BB:CC:DD:EE:FF', lastError: null }, driver: { serialConnected: true, serialPort: '/dev/ttyUSB0', baudRate: 115200, toolingRunning: false, toolingAction: null, toolingPort: null, lastToolExitCode: 0, toolingError: null } } }));
    }

    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  }) as typeof fetch;

  const ports = await fetchPorts();
  const connection = await fetchConnection();
  const logs = await fetchLogs();
  const telemetry = await fetchTelemetry();
  const tooling = await fetchTooling();
  await connectPort('/dev/ttyUSB0', 115200);
  await disconnectPort();
  await sendCommand('f');
  await startBuild();
  await startFlash('/dev/ttyUSB0');
  await pushDebugLog('ping');

  assert.equal(ports[0]?.path, '/dev/ttyUSB0');
  assert.equal(connection.isOpen, true);
  assert.equal(logs[0]?.line, 'hello');
  assert.equal(telemetry.mpu.model, 'MPU9250');
  assert.equal(tooling.projectDir, '/tmp/project');
  assert.ok(calls.some((call) => call.input.endsWith('/api/command') && call.init?.body === JSON.stringify({ command: 'f' })));
  assert.ok(calls.some((call) => call.input.endsWith('/api/tooling/flash') && call.init?.body === JSON.stringify({ portPath: '/dev/ttyUSB0' })));
});

test('createLogsEventSource points to stream endpoint', () => {
  const OriginalEventSource = globalThis.EventSource;
  globalThis.EventSource = FakeEventSource as unknown as typeof EventSource;
  try {
    const source = createLogsEventSource() as unknown as FakeEventSource;
    assert.equal(source.url, '/api/logs/stream');
  } finally {
    globalThis.EventSource = OriginalEventSource;
  }
});
