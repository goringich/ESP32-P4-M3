import { spawn, type ChildProcessWithoutNullStreams } from 'node:child_process';
import type { ToolingAction, ToolingState } from '../types/serial.js';

type ToolingStateListener = (state: ToolingState) => void;
type PushLog = (line: string) => void;
type SpawnedProcess = Pick<ChildProcessWithoutNullStreams, 'stdout' | 'stderr' | 'on'>;
type SpawnFn = (
  command: string,
  args: readonly string[],
  options: {
    cwd: string;
    env: NodeJS.ProcessEnv;
  }
) => SpawnedProcess;
type ToolingManagerOptions = {
  projectDir?: string;
  idfPath?: string;
  exportScript?: string;
  spawnFn?: SpawnFn;
};

const DEFAULT_PROJECT_DIR = process.env.IDF_PROJECT_DIR ?? '/home/goringich/esp/hello_world_p4';
const DEFAULT_IDF_PATH = process.env.IDF_PATH ?? '/home/goringich/esp/esp-idf';
const DEFAULT_EXPORT_SCRIPT = process.env.IDF_EXPORT_SCRIPT ?? `${DEFAULT_IDF_PATH}/export.sh`;

function shellEscape(value: string): string {
  return `'${value.replace(/'/g, `'\\''`)}'`;
}

export class ToolingManager {
  private readonly projectDir: string;
  private readonly idfPath: string;
  private readonly exportScript: string;
  private readonly pushLog: PushLog;
  private readonly spawnFn: SpawnFn;
  private readonly stateListeners = new Set<ToolingStateListener>();
  private currentProcess: SpawnedProcess | null = null;
  private outputBuffers: Record<'stdout' | 'stderr', string> = {
    stdout: '',
    stderr: '',
  };
  private state: ToolingState;

  constructor(pushLog: PushLog, options: ToolingManagerOptions = {}) {
    this.pushLog = pushLog;
    this.projectDir = options.projectDir ?? DEFAULT_PROJECT_DIR;
    this.idfPath = options.idfPath ?? DEFAULT_IDF_PATH;
    this.exportScript = options.exportScript ?? DEFAULT_EXPORT_SCRIPT;
    this.spawnFn = options.spawnFn ?? spawn;
    this.state = {
      isRunning: false,
      currentAction: null,
      lastAction: null,
      lastExitCode: null,
      projectDir: this.projectDir,
      portPath: null,
      startedAt: null,
      finishedAt: null,
      error: null,
    };
  }

  getState(): ToolingState {
    return this.state;
  }

  onState(listener: ToolingStateListener) {
    this.stateListeners.add(listener);

    return () => {
      this.stateListeners.delete(listener);
    };
  }

  startBuild() {
    this.start('build');
  }

  startFlash(portPath: string) {
    if (!portPath.trim()) {
      throw new Error('port path is required for flashing');
    }

    this.start('flash', portPath.trim());
  }

  private start(action: ToolingAction, portPath: string | null = null) {
    if (this.currentProcess) {
      throw new Error(`tooling is already running: ${this.state.currentAction}`);
    }

    const command =
      action === 'build'
        ? 'idf.py build'
        : `idf.py -p ${shellEscape(portPath ?? '')} flash`;

    this.state = {
      ...this.state,
      isRunning: true,
      currentAction: action,
      lastAction: action,
      portPath,
      startedAt: Date.now(),
      finishedAt: null,
      error: null,
    };
    this.emitState();
    this.pushLog(`[tool] starting ${action} in ${this.projectDir}`);

    const processHandle = this.spawnFn(
      '/bin/bash',
      [
        '-lc',
        `export IDF_PATH=${shellEscape(this.idfPath)} && source ${shellEscape(this.exportScript)} >/dev/null 2>&1 && ${command}`,
      ],
      {
        cwd: this.projectDir,
        env: {
          ...process.env,
          IDF_PATH: this.idfPath,
        },
      }
    );

    this.currentProcess = processHandle;
    this.outputBuffers.stdout = '';
    this.outputBuffers.stderr = '';
    this.attachOutput(processHandle, action, 'stdout');
    this.attachOutput(processHandle, action, 'stderr');

    processHandle.on('error', (error) => {
      this.finish(action, null, error.message);
    });

    processHandle.on('close', (code) => {
      this.finish(action, code, code === 0 ? null : `${action} failed with exit code ${code ?? 'unknown'}`);
    });
  }

  private attachOutput(
    processHandle: SpawnedProcess,
    action: ToolingAction,
    stream: 'stdout' | 'stderr'
  ) {
    processHandle[stream].setEncoding('utf8');
    processHandle[stream].on('data', (chunk: string) => {
      const normalized = `${this.outputBuffers[stream]}${chunk.replace(/\r/g, '\n')}`;
      const parts = normalized.split('\n');
      this.outputBuffers[stream] = parts.pop() ?? '';
      for (const line of parts) {
        this.pushOutputLine(action, line);
      }
    });
  }

  private finish(action: ToolingAction, exitCode: number | null, error: string | null) {
    if (this.currentProcess) {
      this.currentProcess = null;
    }

    this.state = {
      ...this.state,
      isRunning: false,
      currentAction: null,
      lastExitCode: exitCode,
      finishedAt: Date.now(),
      error,
    };
    this.emitState();

    this.flushOutputBuffer(action, 'stdout');
    this.flushOutputBuffer(action, 'stderr');

    if (error) {
      this.pushLog(`[tool] ${action} finished with error: ${error}`);
      return;
    }

    this.pushLog(`[tool] ${action} finished successfully`);
  }

  private flushOutputBuffer(action: ToolingAction, stream: 'stdout' | 'stderr') {
    const pending = this.outputBuffers[stream];
    this.outputBuffers[stream] = '';
    if (pending) {
      this.pushOutputLine(action, pending);
    }
  }

  private pushOutputLine(action: ToolingAction, line: string) {
    const trimmed = line.trimEnd();
    if (trimmed) {
      this.pushLog(`[${action}] ${trimmed}`);
    }
  }

  private emitState() {
    for (const listener of this.stateListeners) {
      listener(this.state);
    }
  }
}
