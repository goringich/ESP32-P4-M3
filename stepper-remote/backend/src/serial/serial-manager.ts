import { SerialPort } from 'serialport';
import { ReadlineParser } from '@serialport/parser-readline';
import { randomUUID } from 'node:crypto';
import {
  applyConnectionTelemetry,
  applyLogTelemetry,
  createInitialTelemetryState,
} from '../telemetry/telemetry-parser.js';
import type {
  OpenPortPayload,
  SerialConnectionState,
  SerialLogEntry,
  TelemetryState,
} from '../types/serial.js';

type LogListener = (entry: SerialLogEntry) => void;
type StateListener = (state: SerialConnectionState) => void;
type TelemetryListener = (state: TelemetryState) => void;

const MAX_LOG_BUFFER = 1000;

export class SerialManager {
  private port: SerialPort | null = null;
  private parser: ReadlineParser | null = null;
  private logs: SerialLogEntry[] = [];
  private logListeners = new Set<LogListener>();
  private stateListeners = new Set<StateListener>();
  private telemetryListeners = new Set<TelemetryListener>();
  private state: SerialConnectionState = {
    isOpen: false,
    path: null,
    baudRate: null,
  };
  private telemetry = applyConnectionTelemetry(createInitialTelemetryState(), this.state);

  async listPorts() {
    const ports = await SerialPort.list();

    return ports.map((port) => ({
      path: port.path,
      manufacturer: port.manufacturer ?? '',
      serialNumber: port.serialNumber ?? '',
      vendorId: port.vendorId ?? '',
      productId: port.productId ?? '',
      friendlyName:
        [port.manufacturer, port.path].filter(Boolean).join(' - ') || port.path,
    }));
  }

  getLogs() {
    return this.logs;
  }

  getState() {
    return this.state;
  }

  getTelemetry() {
    return this.telemetry;
  }

  pushSystemLog(line: string) {
    this.pushLog(line);
  }

  onLog(listener: LogListener) {
    this.logListeners.add(listener);

    return () => {
      this.logListeners.delete(listener);
    };
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

  async open(payload: OpenPortPayload) {
    await this.close();

    const port = new SerialPort({
      path: payload.path,
      baudRate: payload.baudRate,
      autoOpen: true,
    });

    const parser = port.pipe(
      new ReadlineParser({
        delimiter: '\n',
        encoding: 'utf8',
      })
    );

    this.port = port;
    this.parser = parser;

    port.on('open', () => {
      this.state = {
        isOpen: true,
        path: payload.path,
        baudRate: payload.baudRate,
      };
      this.emitState();
      this.pushLog(`[host] port opened: ${payload.path} @ ${payload.baudRate}`);
    });

    port.on('close', () => {
      this.pushLog('[host] port closed');
      this.state = {
        isOpen: false,
        path: null,
        baudRate: null,
      };
      this.emitState();
    });

    port.on('error', (error) => {
      this.pushLog(`[host] serial error: ${error.message}`);
    });

    parser.on('data', (line: string) => {
      const normalized = line.replace(/\r/g, '');
      this.pushLog(normalized);
    });
  }

  async close() {
    if (!this.port) {
      return;
    }

    const currentPort = this.port;
    this.port = null;
    this.parser = null;

    if (currentPort.isOpen) {
      await new Promise<void>((resolve, reject) => {
        currentPort.close((error) => {
          if (error) {
            reject(error);
            return;
          }

          resolve();
        });
      });
    }
  }

  async send(command: string) {
    if (!this.port || !this.state.isOpen) {
      throw new Error('serial port is not open');
    }

    const trimmed = command.trim();
    if (!trimmed) {
      throw new Error('command is empty');
    }

    await new Promise<void>((resolve, reject) => {
      this.port!.write(trimmed, (error) => {
        if (error) {
          reject(error);
          return;
        }

        this.port!.drain((drainError) => {
          if (drainError) {
            reject(drainError);
            return;
          }

          resolve();
        });
      });
    });

    this.pushLog(`[tx] ${trimmed}`);
  }

  private pushLog(line: string) {
    const entry: SerialLogEntry = {
      id: randomUUID(),
      ts: Date.now(),
      line,
    };

    this.logs.push(entry);

    if (this.logs.length > MAX_LOG_BUFFER) {
      this.logs.splice(0, this.logs.length - MAX_LOG_BUFFER);
    }

    for (const listener of this.logListeners) {
      listener(entry);
    }

    const nextTelemetry = applyLogTelemetry(this.telemetry, line, entry.ts);
    if (nextTelemetry !== this.telemetry) {
      this.telemetry = nextTelemetry;
      this.emitTelemetry();
    }
  }

  private emitState() {
    this.telemetry = applyConnectionTelemetry(this.telemetry, this.state);

    for (const listener of this.stateListeners) {
      listener(this.state);
    }

    this.emitTelemetry();
  }

  private emitTelemetry() {
    for (const listener of this.telemetryListeners) {
      listener(this.telemetry);
    }
  }
}
