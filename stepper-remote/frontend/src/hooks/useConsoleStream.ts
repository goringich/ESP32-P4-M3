import { useEffect, useRef, useState } from 'react';
import {
  createLogsEventSource,
  fetchConnection,
  fetchLogs,
  fetchTelemetry,
  fetchTooling,
} from '../api/client';
import type {
  ConnectionState,
  LogEntry,
  StreamStatus,
  TelemetryState,
  ToolingState,
} from '../types/api';

const EMPTY_CONNECTION: ConnectionState = {
  isOpen: false,
  path: null,
  baudRate: null,
};

const EMPTY_TOOLING: ToolingState = {
  isRunning: false,
  currentAction: null,
  lastAction: null,
  lastExitCode: null,
  error: null,
  portPath: null,
  projectDir: null,
};

const EMPTY_TELEMETRY: TelemetryState = {
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
    address: null,
    whoAmI: null,
    model: null,
    tempC: null,
    accel: { x: null, y: null, z: null },
    gyro: { x: null, y: null, z: null },
    error: null,
  },
  stepper: {
    mode: null,
    sweepState: null,
    lastCommand: null,
    delayMs: null,
    stepsPerSecond: null,
    phaseIndex: null,
    totalSteps: null,
    coilsEnabled: null,
    uartReady: null,
    pins: {
      in1: null,
      in2: null,
      in3: null,
      in4: null,
    },
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

export function useConsoleStream() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [connection, setConnection] = useState<ConnectionState>(EMPTY_CONNECTION);
  const [tooling, setTooling] = useState<ToolingState>(EMPTY_TOOLING);
  const [telemetry, setTelemetry] = useState<TelemetryState>(EMPTY_TELEMETRY);
  const [streamStatus, setStreamStatus] = useState<StreamStatus>('connecting');
  const [streamError, setStreamError] = useState<string | null>(null);

  const streamFailedRef = useRef(false);

  useEffect(() => {
    let disposed = false;
    let source: EventSource | null = null;
    let pollingTimer: number | null = null;

    const syncSnapshot = async () => {
      try {
        const [nextLogs, nextConnection, nextTooling, nextTelemetry] = await Promise.all([
          fetchLogs(),
          fetchConnection(),
          fetchTooling(),
          fetchTelemetry(),
        ]);

        if (disposed) {
          return;
        }

        setLogs(nextLogs);
        setConnection(nextConnection);
        setTooling(nextTooling);
        setTelemetry(nextTelemetry);
        setStreamError(null);
      } catch (error) {
        if (disposed) {
          return;
        }

        setStreamError(
          error instanceof Error ? error.message : 'Unable to reach backend'
        );
      }
    };

    const startPolling = () => {
      if (pollingTimer !== null) {
        return;
      }

      setStreamStatus('fallback');

      void syncSnapshot();

      pollingTimer = window.setInterval(() => {
        void syncSnapshot();
      }, 2500);
    };

    const startStream = () => {
      setStreamStatus('connecting');

      try {
        source = createLogsEventSource();
      } catch (error) {
        setStreamError(
          error instanceof Error ? error.message : 'Unable to start event stream'
        );
        startPolling();
        return;
      }

      source.addEventListener('open', () => {
        if (disposed) {
          return;
        }

        setStreamStatus('live');
        setStreamError(null);
        streamFailedRef.current = false;
      });

      source.addEventListener('log', (event) => {
        const message = JSON.parse((event as MessageEvent).data) as LogEntry;

        setLogs((prev) => {
          const next = [...prev, message];
          if (next.length > 1200) {
            return next.slice(next.length - 1200);
          }
          return next;
        });
      });

      source.addEventListener('state', (event) => {
        const state = JSON.parse((event as MessageEvent).data) as ConnectionState;
        setConnection(state);
      });

      source.onerror = () => {
        if (disposed) {
          return;
        }

        source?.close();
        source = null;

        if (!streamFailedRef.current) {
          streamFailedRef.current = true;
          setStreamStatus('reconnecting');
          setStreamError('Live stream is unavailable, switched to polling mode.');
        }

        startPolling();
      };
    };

    void syncSnapshot();
    startStream();

    return () => {
      disposed = true;

      if (source) {
        source.close();
      }

      if (pollingTimer !== null) {
        window.clearInterval(pollingTimer);
      }
    };
  }, []);

  return {
    logs,
    connection,
    tooling,
    telemetry,
    streamStatus,
    streamError,
    setConnection,
  };
}