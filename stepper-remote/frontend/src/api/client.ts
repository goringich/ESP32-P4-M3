import type {
  ConnectionState,
  LogEntry,
  TelemetryState,
  ToolingState,
  PortInfo,
  StreamStatus,
} from '../types/api';

type ApiSuccess<T> = {
  ok: true;
} & T;

type ApiError = {
  ok: false;
  error?: string;
};

type ApiResponse<T> = ApiSuccess<T> | ApiError;

async function apiRequest<T>(input: string, init?: RequestInit): Promise<T> {
  let response: Response;

  try {
    response = await fetch(input, init);
  } catch (error) {
    throw new Error(
      error instanceof Error
        ? `backend is unavailable: ${error.message}`
        : 'backend is unavailable'
    );
  }

  let data: ApiResponse<T>;

  try {
    data = (await response.json()) as ApiResponse<T>;
  } catch {
    throw new Error(`invalid backend response for ${input}`);
  }

  if (!response.ok || !data.ok) {
    const message =
      'error' in data && typeof data.error === 'string'
        ? data.error
        : `request failed: ${response.status}`;
    throw new Error(message);
  }

  return data as T;
}

export async function fetchPorts(): Promise<PortInfo[]> {
  const data = await apiRequest<{ ports: PortInfo[] }>('/api/ports');
  return data.ports;
}

export async function fetchConnection(): Promise<ConnectionState> {
  const data = await apiRequest<{ connection: ConnectionState }>('/api/connection');
  return data.connection;
}

export async function fetchLogs(): Promise<LogEntry[]> {
  const data = await apiRequest<{ logs: LogEntry[] }>('/api/logs');
  return data.logs;
}

export async function fetchTooling(): Promise<ToolingState> {
  const data = await apiRequest<{ tooling: ToolingState }>('/api/tooling');
  return data.tooling;
}

export async function fetchTelemetry(): Promise<TelemetryState> {
  const data = await apiRequest<{ telemetry: TelemetryState }>('/api/telemetry');
  return data.telemetry;
}

export async function connectPort(path: string, baudRate: number) {
  await apiRequest<{ connection: ConnectionState }>('/api/connect', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ path, baudRate }),
  });
}

export async function disconnectPort() {
  await apiRequest<{ connection: ConnectionState }>('/api/disconnect', {
    method: 'POST',
  });
}

export async function sendCommand(command: string) {
  await apiRequest<Record<string, never>>('/api/command', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ command }),
  });
}

export async function startBuild() {
  await apiRequest<Record<string, never>>('/api/tooling/build', {
    method: 'POST',
  });
}

export async function startFlash(portPath: string) {
  await apiRequest<Record<string, never>>('/api/tooling/flash', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ portPath }),
  });
}

export async function pushDebugLog() {
  await apiRequest<Record<string, never>>('/api/debug/log', {
    method: 'POST',
  });
}

export function createLogsEventSource() {
  return new EventSource('/api/logs/stream');
}

export type { StreamStatus };