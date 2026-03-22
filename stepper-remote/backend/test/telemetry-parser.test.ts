import test from 'node:test';
import assert from 'node:assert/strict';
import {
  applyConnectionTelemetry,
  applyLogTelemetry,
  applyToolingTelemetry,
  createInitialTelemetryState,
} from '../src/telemetry/telemetry-parser.js';

test('telemetry parser ingests structured MCU lines', () => {
  let state = createInitialTelemetryState();

  state = applyLogTelemetry(
    state,
    '@telemetry {"kind":"system","uptime_ms":1250,"tick":3,"tick_delay_ms":5,"firmware":"hello_world_p4","app_mode":"l293d_test"}',
    10
  );
  state = applyLogTelemetry(
    state,
    '@telemetry {"kind":"mpu","ready":true,"address":"0x68","whoami":"0x71","model":"MPU9250","uptime":"00:01","accel":{"x_g":0.1,"y_g":0.2,"z_g":0.3},"gyro":{"x_dps":1.1,"y_dps":2.2,"z_dps":3.3},"temp_c":29.5}',
    20
  );
  state = applyLogTelemetry(
    state,
    '@telemetry {"kind":"stepper","mode":"forward","sweep_state":"forward","step_delay_ms":80,"steps_per_second":12.5,"phase_index":2,"total_steps":99,"coils_enabled":true,"sweep_steps":17,"uart_ready":true,"last_command":"f","pins":{"in1":18,"in2":19,"in3":21,"in4":22},"led_gpio":2}',
    30
  );

  assert.equal(state.system.firmware, 'hello_world_p4');
  assert.equal(state.system.tick, 3);
  assert.equal(state.mpu.model, 'MPU9250');
  assert.equal(state.mpu.accel.z, 0.3);
  assert.equal(state.stepper.mode, 'forward');
  assert.equal(state.stepper.totalSteps, 99);
  assert.equal(state.stepper.pins.in4, 22);
});

test('telemetry parser derives i2c and wifi state from plain logs', () => {
  let state = createInitialTelemetryState();

  state = applyLogTelemetry(state, 'I (101) i2c_bus: scan: found 0x68', 100);
  state = applyLogTelemetry(state, 'I (102) i2c_bus: scan: result found=1 timeouts=0 other_err=0', 101);
  state = applyLogTelemetry(state, 'W (110) app: mpu: addr=0x68 WHO_AM_I=0x71 (MPU9250)', 102);
  state = applyLogTelemetry(state, "I (200) app_wifi: connect success to 'lab'", 103);
  state = applyLogTelemetry(state, 'I (220) app_wifi: got ip: 192.168.0.10', 104);

  assert.deepEqual(state.i2c.devices, ['0X68']);
  assert.equal(state.i2c.lastScanSummary, 'found=1, timeouts=0, other=0');
  assert.equal(state.i2c.detectedMpuAddress, '0X68');
  assert.equal(state.wifi.ssid, 'lab');
  assert.equal(state.wifi.ip, '192.168.0.10');
});

test('telemetry parser tracks driver state from serial and tooling', () => {
  let state = createInitialTelemetryState();

  state = applyConnectionTelemetry(state, {
    isOpen: true,
    path: '/dev/ttyUSB0',
    baudRate: 115200,
  });
  state = applyToolingTelemetry(state, {
    isRunning: true,
    currentAction: 'flash',
    lastAction: 'flash',
    lastExitCode: null,
    projectDir: '/tmp/project',
    portPath: '/dev/ttyUSB0',
    startedAt: 1,
    finishedAt: null,
    error: null,
  });

  assert.equal(state.driver.serialConnected, true);
  assert.equal(state.driver.serialPort, '/dev/ttyUSB0');
  assert.equal(state.driver.toolingAction, 'flash');
});
