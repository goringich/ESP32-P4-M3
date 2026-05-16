import test from 'node:test';
import assert from 'node:assert/strict';
import { WifiBridgeManager } from '../src/remote/wifi-bridge.js';

type MockResponse = {
  ok: boolean;
  status: number;
  json: () => Promise<unknown>;
};

function createJsonResponse(payload: unknown, status = 200): MockResponse {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => payload,
  };
}

test('WifiBridgeManager polls telemetry and sends commands through MCU API', async () => {
  const logs: string[] = [];
  const calls: Array<{ url: string; init?: RequestInit }> = [];
  const originalFetch = globalThis.fetch;

  globalThis.fetch = (async (input: string | URL | Request, init?: RequestInit) => {
    const url = typeof input === 'string' ? input : String(input);
    calls.push({ url, init });

    if (url.endsWith('/api/telemetry')) {
      return createJsonResponse({
        ok: true,
        telemetry: {
          system: {
            firmware: 'p4_lab',
            appMode: 'l293d_test',
            uptimeMs: 1234,
          },
          stepper: {
            mode: 'stop',
            lastCommand: 's',
            pins: { in1: 0, in2: 0, in3: 0, in4: 0 },
            gpioPins: { in1: 3, in2: 4, in3: 5, in4: 20 },
          },
          wifi: {
            connected: true,
            apStarted: true,
            apSsid: 'JC-ESP32P4M3',
            apIp: '192.168.4.1',
          },
        },
      }) as unknown as Response;
    }

    if (url.endsWith('/api/command')) {
      return createJsonResponse({ ok: true }) as unknown as Response;
    }

    throw new Error(`unexpected fetch: ${url}`);
  }) as typeof fetch;

  try {
    const manager = new WifiBridgeManager((line) => logs.push(line));

    const state = await manager.configure({
      mode: 'wifi',
      wifiBaseUrl: 'http://192.168.4.1/',
    });

    assert.equal(state.mode, 'wifi');
    assert.equal(state.wifiBaseUrl, 'http://192.168.4.1');
    assert.equal(state.wifiConnected, true);
    assert.equal(manager.getTelemetry().system.firmware, 'p4_lab');
    assert.equal(manager.getTelemetry().wifi.apIp, '192.168.4.1');
    assert.equal(manager.getTelemetry().stepper.gpioPins.in4, 20);

    await manager.sendCommand('f');

    assert.ok(calls.some((call) => call.url === 'http://192.168.4.1/api/telemetry'));
    assert.ok(calls.some((call) => call.url === 'http://192.168.4.1/api/command'));
    assert.ok(logs.some((line) => line.includes('[wifi] bridge is live')));

    await manager.configure({ mode: 'serial' });
  } finally {
    globalThis.fetch = originalFetch;
  }
});

test('WifiBridgeManager reports telemetry failures and resets on serial return', async () => {
  const logs: string[] = [];
  const originalFetch = globalThis.fetch;

  globalThis.fetch = (async () => {
    return createJsonResponse({ ok: false }, 503) as unknown as Response;
  }) as typeof fetch;

  try {
    const manager = new WifiBridgeManager((line) => logs.push(line));

    const wifiState = await manager.configure({
      mode: 'wifi',
      wifiBaseUrl: 'http://10.0.0.1',
    });

    assert.equal(wifiState.mode, 'wifi');
    assert.equal(wifiState.wifiConnected, false);
    assert.match(wifiState.lastError ?? '', /503/);
    assert.ok(logs.some((line) => line.includes('[wifi] bridge error')));

    const serialState = await manager.configure({ mode: 'serial' });
    assert.equal(serialState.mode, 'serial');
    assert.equal(serialState.wifiConnected, false);
    assert.equal(serialState.lastError, null);
  } finally {
    globalThis.fetch = originalFetch;
  }
});
