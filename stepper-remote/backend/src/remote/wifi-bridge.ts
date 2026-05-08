import { createInitialTelemetryState } from '../telemetry/telemetry-parser.js';
import type {
  TelemetryState,
  TransportMode,
  TransportState,
} from '../types/serial.js';

type PushLog = (line: string) => void;
type StateListener = (state: TransportState) => void;
type TelemetryListener = (state: TelemetryState) => void;

type RemotePayload = {
  ok: boolean;
  telemetry?: {
    system?: {
      uptimeMs?: number | null;
      tick?: number | null;
      tickDelayMs?: number | null;
      firmware?: string | null;
      appMode?: string | null;
      lastError?: string | null;
    };
    mpu?: {
      ready?: boolean | null;
      error?: string | null;
      address?: string | null;
      whoAmI?: string | null;
      model?: string | null;
      uptimeLabel?: string | null;
      accel?: { x?: number | null; y?: number | null; z?: number | null };
      gyro?: { x?: number | null; y?: number | null; z?: number | null };
      tempC?: number | null;
    };
    i2c?: {
      ready?: boolean | null;
      devices?: string[];
      detectedMpuAddress?: string | null;
      lastScanSummary?: string | null;
      error?: string | null;
    };
    stepper?: TelemetryState['stepper'];
    wifi?: {
      enabled?: boolean | null;
      connected?: boolean | null;
      ssid?: string | null;
      ip?: string | null;
      mac?: string | null;
      lastError?: string | null;
      initialized?: boolean | null;
      apStarted?: boolean | null;
      staAttempted?: boolean | null;
      staConnected?: boolean | null;
      apSsid?: string | null;
      apIp?: string | null;
      staIp?: string | null;
    };
  };
};

const DEFAULT_WIFI_BASE_URL = process.env.ESP_WIFI_BASE_URL ?? 'http://192.168.4.1';
const WIFI_POLL_INTERVAL_MS = 1000;

function normalizeBaseUrl(value: string) {
  return value.trim().replace(/\/+$/, '') || DEFAULT_WIFI_BASE_URL;
}

function cloneTransportState(state: TransportState): TransportState {
  return { ...state };
}

export class WifiBridgeManager {
  private readonly pushLog: PushLog;
  private readonly stateListeners = new Set<StateListener>();
  private readonly telemetryListeners = new Set<TelemetryListener>();
  private state: TransportState = {
    mode: 'serial',
    wifiBaseUrl: normalizeBaseUrl(DEFAULT_WIFI_BASE_URL),
    wifiConnected: false,
    lastError: null,
    lastTelemetryAt: null,
  };
  private telemetry = createInitialTelemetryState();
  private pollTimer: ReturnType<typeof setInterval> | null = null;
  private announcedWifiReady = false;

  constructor(pushLog: PushLog) {
    this.pushLog = pushLog;
  }

  getState() {
    return cloneTransportState(this.state);
  }

  getTelemetry() {
    return this.telemetry;
  }

  onState(listener: StateListener) {
    this.stateListeners.add(listener);
    return () => {
      this.stateListeners.delete(listener);
    };
  }

  onTelemetry(listener: TelemetryListener) {
    this.telemetryListeners.add(listener);
    return () => {
      this.telemetryListeners.delete(listener);
    };
  }

  async configure(next: { mode?: TransportMode; wifiBaseUrl?: string }) {
    const previousMode = this.state.mode;
    const previousUrl = this.state.wifiBaseUrl;

    this.state = {
      ...this.state,
      mode: next.mode ?? this.state.mode,
      wifiBaseUrl: next.wifiBaseUrl
        ? normalizeBaseUrl(next.wifiBaseUrl)
        : this.state.wifiBaseUrl,
    };

    if (this.state.mode !== previousMode || this.state.wifiBaseUrl !== previousUrl) {
      this.emitState();
    }

    if (this.state.mode === 'wifi') {
      this.startPolling();
      await this.pollOnce();
      return this.getState();
    }

    this.stopPolling();
    this.state = {
      ...this.state,
      wifiConnected: false,
      lastError: null,
    };
    this.announcedWifiReady = false;
    this.emitState();
    return this.getState();
  }

  async sendCommand(command: string) {
    const url = `${this.state.wifiBaseUrl}/api/command`;
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ command }),
      signal: AbortSignal.timeout(2000),
    });

    if (!response.ok) {
      throw new Error(`wifi command failed: ${response.status}`);
    }

    await this.pollOnce();
  }

  private startPolling() {
    if (this.pollTimer !== null) {
      return;
    }

    this.pollTimer = setInterval(() => {
      void this.pollOnce();
    }, WIFI_POLL_INTERVAL_MS);
  }

  private stopPolling() {
    if (this.pollTimer === null) {
      return;
    }

    clearInterval(this.pollTimer);
    this.pollTimer = null;
  }

  private async pollOnce() {
    try {
      const response = await fetch(`${this.state.wifiBaseUrl}/api/telemetry`, {
        signal: AbortSignal.timeout(1800),
      });

      if (!response.ok) {
        throw new Error(`wifi telemetry failed: ${response.status}`);
      }

      const payload = (await response.json()) as RemotePayload;
      if (!payload.ok || !payload.telemetry) {
        throw new Error('wifi telemetry payload is invalid');
      }

      this.telemetry = this.mapRemoteTelemetry(payload.telemetry);
      this.state = {
        ...this.state,
        wifiConnected: true,
        lastError: null,
        lastTelemetryAt: Date.now(),
      };
      this.emitState();
      this.emitTelemetry();

      if (!this.announcedWifiReady) {
        this.pushLog(`[wifi] bridge is live at ${this.state.wifiBaseUrl}`);
        this.announcedWifiReady = true;
      }
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'unknown wifi transport error';
      const nextState = {
        ...this.state,
        wifiConnected: false,
        lastError: message,
      };
      const changed =
        nextState.wifiConnected !== this.state.wifiConnected ||
        nextState.lastError !== this.state.lastError;

      this.state = nextState;
      this.emitState();

      if (changed) {
        this.pushLog(`[wifi] bridge error: ${message}`);
      }
    }
  }

  private mapRemoteTelemetry(remote: NonNullable<RemotePayload['telemetry']>) {
    const next = createInitialTelemetryState();

    if (remote.system) {
      next.system.uptimeMs = remote.system.uptimeMs ?? null;
      next.system.tick = remote.system.tick ?? null;
      next.system.tickDelayMs = remote.system.tickDelayMs ?? null;
      next.system.firmware = remote.system.firmware ?? null;
      next.system.appMode = remote.system.appMode ?? null;
      next.system.lastError = remote.system.lastError ?? null;
    }

    if (remote.mpu) {
      next.mpu.ready = remote.mpu.ready ?? null;
      next.mpu.error = remote.mpu.error ?? null;
      next.mpu.address = remote.mpu.address ?? null;
      next.mpu.whoAmI = remote.mpu.whoAmI ?? null;
      next.mpu.model = remote.mpu.model ?? null;
      next.mpu.uptimeLabel = remote.mpu.uptimeLabel ?? null;
      next.mpu.accel.x = remote.mpu.accel?.x ?? null;
      next.mpu.accel.y = remote.mpu.accel?.y ?? null;
      next.mpu.accel.z = remote.mpu.accel?.z ?? null;
      next.mpu.gyro.x = remote.mpu.gyro?.x ?? null;
      next.mpu.gyro.y = remote.mpu.gyro?.y ?? null;
      next.mpu.gyro.z = remote.mpu.gyro?.z ?? null;
      next.mpu.tempC = remote.mpu.tempC ?? null;
    }

    if (remote.i2c) {
      next.i2c.ready = remote.i2c.ready ?? null;
      next.i2c.devices = remote.i2c.devices ?? [];
      next.i2c.detectedMpuAddress = remote.i2c.detectedMpuAddress ?? null;
      next.i2c.lastScanSummary = remote.i2c.lastScanSummary ?? null;
      next.i2c.error = remote.i2c.error ?? null;
    }

    if (remote.stepper) {
      next.stepper = {
        ...next.stepper,
        ...remote.stepper,
        pins: {
          in1: remote.stepper.pins?.in1 ?? null,
          in2: remote.stepper.pins?.in2 ?? null,
          in3: remote.stepper.pins?.in3 ?? null,
          in4: remote.stepper.pins?.in4 ?? null,
        },
      };
    }

    if (remote.wifi) {
      next.wifi.enabled = remote.wifi.enabled ?? remote.wifi.initialized ?? null;
      next.wifi.connected = remote.wifi.connected ?? remote.wifi.apStarted ?? null;
      next.wifi.ssid = remote.wifi.ssid ?? remote.wifi.apSsid ?? null;
      next.wifi.ip = remote.wifi.ip ?? remote.wifi.staIp ?? remote.wifi.apIp ?? null;
      next.wifi.mac = remote.wifi.mac ?? null;
      next.wifi.lastError = remote.wifi.lastError ?? null;
      next.wifi.initialized = remote.wifi.initialized ?? null;
      next.wifi.apStarted = remote.wifi.apStarted ?? null;
      next.wifi.staAttempted = remote.wifi.staAttempted ?? null;
      next.wifi.staConnected = remote.wifi.staConnected ?? null;
      next.wifi.apSsid = remote.wifi.apSsid ?? null;
      next.wifi.apIp = remote.wifi.apIp ?? null;
      next.wifi.staIp = remote.wifi.staIp ?? null;
    }

    next.updatedAt = Date.now();
    return next;
  }

  private emitState() {
    const state = this.getState();
    for (const listener of this.stateListeners) {
      listener(state);
    }
  }

  private emitTelemetry() {
    for (const listener of this.telemetryListeners) {
      listener(this.telemetry);
    }
  }
}
