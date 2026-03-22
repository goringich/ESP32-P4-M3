export type SerialLogEntry = {
  id: string;
  ts: number;
  line: string;
};

export type TelemetrySystemState = {
  uptimeMs: number | null;
  tick: number | null;
  tickDelayMs: number | null;
  firmware: string | null;
  appMode: string | null;
  lastError: string | null;
};

export type TelemetryMpuState = {
  ready: boolean | null;
  error: string | null;
  address: string | null;
  whoAmI: string | null;
  model: string | null;
  uptimeLabel: string | null;
  accel: {
    x: number | null;
    y: number | null;
    z: number | null;
  };
  gyro: {
    x: number | null;
    y: number | null;
    z: number | null;
  };
  tempC: number | null;
};

export type TelemetryStepperState = {
  mode: string | null;
  sweepState: string | null;
  delayMs: number | null;
  stepsPerSecond: number | null;
  phaseIndex: number | null;
  totalSteps: number | null;
  coilsEnabled: boolean | null;
  sweepSteps: number | null;
  uartReady: boolean | null;
  lastCommand: string | null;
  pins: {
    in1: number | null;
    in2: number | null;
    in3: number | null;
    in4: number | null;
  };
  ledGpio: number | null;
};

export type TelemetryI2cState = {
  ready: boolean | null;
  devices: string[];
  detectedMpuAddress: string | null;
  lastScanSummary: string | null;
  error: string | null;
};

export type TelemetryWifiState = {
  enabled: boolean | null;
  connected: boolean | null;
  ssid: string | null;
  ip: string | null;
  mac: string | null;
  lastError: string | null;
};

export type TelemetryDriverState = {
  serialConnected: boolean;
  serialPort: string | null;
  baudRate: number | null;
  toolingRunning: boolean;
  toolingAction: ToolingAction | null;
  toolingPort: string | null;
  lastToolExitCode: number | null;
  toolingError: string | null;
};

export type TelemetryState = {
  updatedAt: number | null;
  system: TelemetrySystemState;
  mpu: TelemetryMpuState;
  stepper: TelemetryStepperState;
  i2c: TelemetryI2cState;
  wifi: TelemetryWifiState;
  driver: TelemetryDriverState;
};

export type SerialConnectionState = {
  isOpen: boolean;
  path: string | null;
  baudRate: number | null;
};

export type OpenPortPayload = {
  path: string;
  baudRate: number;
};

export type SendCommandPayload = {
  command: string;
};

export type ToolingAction = 'build' | 'flash';

export type ToolingState = {
  isRunning: boolean;
  currentAction: ToolingAction | null;
  lastAction: ToolingAction | null;
  lastExitCode: number | null;
  projectDir: string;
  portPath: string | null;
  startedAt: number | null;
  finishedAt: number | null;
  error: string | null;
};

export type FlashPayload = {
  portPath: string;
};
