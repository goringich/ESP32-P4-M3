import test from 'node:test';
import assert from 'node:assert/strict';
import { EventEmitter } from 'node:events';
import { PassThrough } from 'node:stream';
import { ToolingManager } from '../src/tooling/tooling-manager.js';

class FakeProcess extends EventEmitter {
  stdout = new PassThrough();
  stderr = new PassThrough();
}

test('ToolingManager starts build and records successful completion', async () => {
  const logs: string[] = [];
  const spawned: Array<{ command: string; args: readonly string[] }> = [];
  const processHandle = new FakeProcess();

  const manager = new ToolingManager(
    (line) => logs.push(line),
    {
      projectDir: '/tmp/project',
      idfPath: '/tmp/idf',
      exportScript: '/tmp/idf/export.sh',
      spawnFn: (command, args) => {
        spawned.push({ command, args });
        return processHandle;
      },
    }
  );

  manager.startBuild();

  assert.equal(manager.getState().isRunning, true);
  assert.equal(manager.getState().currentAction, 'build');
  assert.equal(spawned.length, 1);
  assert.equal(spawned[0]?.command, '/bin/bash');
  assert.match(String(spawned[0]?.args[1]), /idf\.py build/);

  processHandle.stdout.write('build line 1\nbuild line 2\n');
  processHandle.emit('close', 0);
  await new Promise((resolve) => setImmediate(resolve));

  assert.equal(manager.getState().isRunning, false);
  assert.equal(manager.getState().lastExitCode, 0);
  assert.equal(manager.getState().error, null);
  assert.ok(logs.some((line) => line.includes('[build] build line 1')));
  assert.ok(logs.some((line) => line.includes('[tool] build finished successfully')));
});

test('ToolingManager starts flash with port path and rejects parallel start', () => {
  const processHandle = new FakeProcess();
  const manager = new ToolingManager(() => undefined, {
    spawnFn: () => processHandle,
  });

  manager.startFlash('/dev/ttyUSB0');

  assert.equal(manager.getState().currentAction, 'flash');
  assert.equal(manager.getState().portPath, '/dev/ttyUSB0');
  assert.throws(() => manager.startBuild(), /already running/);
});

test('ToolingManager records failed process exit and validates flash input', async () => {
  const logs: string[] = [];
  const processHandle = new FakeProcess();
  const manager = new ToolingManager((line) => logs.push(line), {
    spawnFn: () => processHandle,
  });

  assert.throws(() => manager.startFlash('   '), /port path is required/);

  manager.startBuild();
  processHandle.stderr.write('boom\n');
  processHandle.emit('close', 7);
  await new Promise((resolve) => setImmediate(resolve));

  assert.equal(manager.getState().isRunning, false);
  assert.equal(manager.getState().lastExitCode, 7);
  assert.match(manager.getState().error ?? '', /exit code 7/);
  assert.ok(logs.some((line) => line.includes('[build] boom')));
});

test('ToolingManager keeps carriage-return progress lines from flash output', async () => {
  const logs: string[] = [];
  const processHandle = new FakeProcess();
  const manager = new ToolingManager((line) => logs.push(line), {
    spawnFn: () => processHandle,
  });

  manager.startFlash('/dev/ttyUSB0');
  processHandle.stdout.write('Writing at 0x00001000... (10 %)\rWriting at 0x00002000... (20 %)\r');
  processHandle.stdout.write('Hash of data verified.\n');
  processHandle.emit('close', 0);
  await new Promise((resolve) => setImmediate(resolve));

  assert.ok(logs.some((line) => line.includes('(10 %)')));
  assert.ok(logs.some((line) => line.includes('(20 %)')));
  assert.ok(logs.some((line) => line.includes('Hash of data verified.')));
});
