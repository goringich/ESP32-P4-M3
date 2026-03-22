import type {
  SerialConnectionState,
  TelemetryState,
  ToolingState,
} from '../types/serial.js';

const ANSI_PATTERN = /\x1b\[[0-9;]*m/g;

type TelemetryEnvelope =
  | {
      kind: 'system';
      uptime_ms: number;
      tick: number;
      tick_delay_ms: number;
      firmware?: string;
      app_mode?: string;
      error?: string | null;
    }
  | {
      kind: 'mpu';
      ready: boolean;
      error?: string | null;
      address?: string | null;
      whoami?: string | null;
      model?: string | null;
      uptime?: string | null;
      accel?: { x_g: number; y_g: number; z_g: number };
      gyro?: { x_dps: number; y_dps: number; z_dps: number };
      temp_c?: number | null;
    }
  | {
      kind: 'stepper';
      mode?: string | null;
      sweep_state?: string | null;
      step_delay_ms?: number | null;
      steps_per_second?: number | null;
      phase_index?: number | null;
      total_steps?: number | null;
      coils_enabled?: boolean | null;
      sweep_steps?: number | null;
      uart_ready?: boolean | null;
      last_command?: string | null;
      pins?: { in1: number; in2: number; in3: number; in4: number };
      led_gpio?: number | null;
    };

function cloneTelemetry(state: TelemetryState): TelemetryState {
  return {
    ...state,
    system: { ...state.system },
    mpu: {
      ...state.mpu,
      accel: { ...state.mpu.accel },
      gyro: { ...state.mpu.gyro },
    },
    stepper: {
      ...state.stepper,
      pins: { ...state.stepper.pins },
    },
    i2c: {
      ...state.i2c,
      devices: [...state.i2c.devices],
    },
    wifi: { ...state.wifi },
    driver: { ...state.driver },
  };
}

export function createInitialTelemetryState(): TelemetryState {
  return {
    updatedAt: null,
    system: {
      uptimeMs: null,
      tick: null,
      tickDelayMs: null,
      firmware: null,
      appMode: null,
      lastError: null,
    },
    mpu: {
      ready: null,
      error: null,
      address: null,
      whoAmI: null,
      model: null,
      uptimeLabel: null,
      accel: {
        x: null,
        y: null,
        z: null,
      },
      gyro: {
        x: null,
        y: null,
        z: null,
      },
      tempC: null,
    },
    stepper: {
      mode: null,
      sweepState: null,
      delayMs: null,
      stepsPerSecond: null,
      phaseIndex: null,
      totalSteps: null,
      coilsEnabled: null,
      sweepSteps: null,
      uartReady: null,
      lastCommand: null,
      pins: {
        in1: null,
        in2: null,
        in3: null,
        in4: null,
      },
      ledGpio: null,
    },
    i2c: {
      ready: null,
      devices: [],
      detectedMpuAddress: null,
      lastScanSummary: null,
      error: null,
    },
    wifi: {
      enabled: null,
      connected: null,
      ssid: null,
      ip: null,
      mac: null,
      lastError: null,
    },
    driver: {
      serialConnected: false,
      serialPort: null,
      baudRate: null,
      toolingRunning: false,
      toolingAction: null,
      toolingPort: null,
      lastToolExitCode: null,
      toolingError: null,
    },
  };
}

function stripAnsi(line: string) {
  return line.replace(ANSI_PATTERN, '').trim();
}

function parseTelemetryLine(line: string): TelemetryEnvelope | null {
  const match = line.match(/@telemetry\s+(\{.*\})$/);
  if (!match) {
    return null;
  }

  try {
    return JSON.parse(match[1]) as TelemetryEnvelope;
  } catch {
    return null;
  }
}

function applyTelemetryEnvelope(
  state: TelemetryState,
  envelope: TelemetryEnvelope,
  ts: number
): TelemetryState {
  const next = cloneTelemetry(state);
  next.updatedAt = ts;

  if (envelope.kind === 'system') {
    next.system.uptimeMs = envelope.uptime_ms;
    next.system.tick = envelope.tick;
    next.system.tickDelayMs = envelope.tick_delay_ms;
    next.system.firmware = envelope.firmware ?? next.system.firmware;
    next.system.appMode = envelope.app_mode ?? next.system.appMode;
    next.system.lastError = envelope.error ?? null;
    return next;
  }

  if (envelope.kind === 'mpu') {
    next.mpu.ready = envelope.ready;
    next.mpu.error = envelope.error ?? null;
    next.mpu.address = envelope.address ?? null;
    next.mpu.whoAmI = envelope.whoami ?? null;
    next.mpu.model = envelope.model ?? null;
    next.mpu.uptimeLabel = envelope.uptime ?? null;
    next.mpu.accel.x = envelope.accel?.x_g ?? null;
    next.mpu.accel.y = envelope.accel?.y_g ?? null;
    next.mpu.accel.z = envelope.accel?.z_g ?? null;
    next.mpu.gyro.x = envelope.gyro?.x_dps ?? null;
    next.mpu.gyro.y = envelope.gyro?.y_dps ?? null;
    next.mpu.gyro.z = envelope.gyro?.z_dps ?? null;
    next.mpu.tempC = envelope.temp_c ?? null;
    return next;
  }

  next.stepper.mode = envelope.mode ?? null;
  next.stepper.sweepState = envelope.sweep_state ?? null;
  next.stepper.delayMs = envelope.step_delay_ms ?? null;
  next.stepper.stepsPerSecond = envelope.steps_per_second ?? null;
  next.stepper.phaseIndex = envelope.phase_index ?? null;
  next.stepper.totalSteps = envelope.total_steps ?? null;
  next.stepper.coilsEnabled = envelope.coils_enabled ?? null;
  next.stepper.sweepSteps = envelope.sweep_steps ?? null;
  next.stepper.uartReady = envelope.uart_ready ?? null;
  next.stepper.lastCommand = envelope.last_command ?? null;
  next.stepper.pins = {
    in1: envelope.pins?.in1 ?? null,
    in2: envelope.pins?.in2 ?? null,
    in3: envelope.pins?.in3 ?? null,
    in4: envelope.pins?.in4 ?? null,
  };
  next.stepper.ledGpio = envelope.led_gpio ?? null;
  return next;
}

export function applyLogTelemetry(
  state: TelemetryState,
  rawLine: string,
  ts: number
): TelemetryState {
  const telemetry = parseTelemetryLine(rawLine);
  if (telemetry) {
    return applyTelemetryEnvelope(state, telemetry, ts);
  }

  const line = stripAnsi(rawLine);
  if (!line) {
    return state;
  }

  let next = state;

  const i2cFound = line.match(/scan:\s+found\s+(0x[0-9A-Fa-f]{2})/);
  if (i2cFound) {
    next = cloneTelemetry(next);
    next.updatedAt = ts;
    next.i2c.ready = true;
    next.i2c.error = null;
    const addr = i2cFound[1].toUpperCase();
    if (!next.i2c.devices.includes(addr)) {
      next.i2c.devices.push(addr);
    }
  }

  const i2cSummary = line.match(/scan:\s+result\s+found=(\d+)\s+timeouts=(\d+)\s+other_err=(\d+)/);
  if (i2cSummary) {
    if (next === state) {
      next = cloneTelemetry(next);
    }
    next.updatedAt = ts;
    next.i2c.ready = true;
    next.i2c.lastScanSummary = `found=${i2cSummary[1]}, timeouts=${i2cSummary[2]}, other=${i2cSummary[3]}`;
    next.i2c.error = null;
  }

  const mpuFound = line.match(/mpu:\s+addr=(0x[0-9A-Fa-f]{2})\s+WHO_AM_I=(0x[0-9A-Fa-f]{2})\s+\(([^)]+)\)/);
  if (mpuFound) {
    if (next === state) {
      next = cloneTelemetry(next);
    }
    next.updatedAt = ts;
    next.i2c.detectedMpuAddress = mpuFound[1].toUpperCase();
    next.mpu.ready = true;
    next.mpu.address = mpuFound[1].toUpperCase();
    next.mpu.whoAmI = mpuFound[2].toUpperCase();
    next.mpu.model = mpuFound[3];
    next.mpu.error = null;
  }

  const mpuMissing = line.match(/mpu:\s+not detected.*\(([^)]+)\)/);
  if (mpuMissing) {
    if (next === state) {
      next = cloneTelemetry(next);
    }
    next.updatedAt = ts;
    next.mpu.ready = false;
    next.mpu.error = mpuMissing[1];
  }

  const wifiIp = line.match(/got ip:\s+([0-9.]+)/);
  if (wifiIp) {
    if (next === state) {
      next = cloneTelemetry(next);
    }
    next.updatedAt = ts;
    next.wifi.enabled = true;
    next.wifi.connected = true;
    next.wifi.ip = wifiIp[1];
    next.wifi.lastError = null;
  }

  const wifiConnect = line.match(/connect success to '([^']+)'/);
  if (wifiConnect) {
    if (next === state) {
      next = cloneTelemetry(next);
    }
    next.updatedAt = ts;
    next.wifi.enabled = true;
    next.wifi.connected = true;
    next.wifi.ssid = wifiConnect[1];
    next.wifi.lastError = null;
  }

  const wifiFail = line.match(/connect (?:failed|timeout) to '([^']+)'/);
  if (wifiFail) {
    if (next === state) {
      next = cloneTelemetry(next);
    }
    next.updatedAt = ts;
    next.wifi.enabled = true;
    next.wifi.connected = false;
    next.wifi.ssid = wifiFail[1];
    next.wifi.lastError = line;
  }

  const wifiMac = line.match(/mac=([0-9A-Fa-f:]{17})/);
  if (wifiMac) {
    if (next === state) {
      next = cloneTelemetry(next);
    }
    next.updatedAt = ts;
    next.wifi.mac = wifiMac[1];
  }

  const systemError = line.match(/tick \d+ \(mpu log err: ([^)]+)\)/);
  if (systemError) {
    if (next === state) {
      next = cloneTelemetry(next);
    }
    next.updatedAt = ts;
    next.system.lastError = systemError[1];
  }

  return next;
}

export function applyConnectionTelemetry(
  state: TelemetryState,
  connection: SerialConnectionState
): TelemetryState {
  const next = cloneTelemetry(state);
  next.driver.serialConnected = connection.isOpen;
  next.driver.serialPort = connection.path;
  next.driver.baudRate = connection.baudRate;
  return next;
}

export function applyToolingTelemetry(
  state: TelemetryState,
  tooling: ToolingState
): TelemetryState {
  const next = cloneTelemetry(state);
  next.driver.toolingRunning = tooling.isRunning;
  next.driver.toolingAction = tooling.currentAction;
  next.driver.toolingPort = tooling.portPath;
  next.driver.lastToolExitCode = tooling.lastExitCode;
  next.driver.toolingError = tooling.error;
  return next;
}
