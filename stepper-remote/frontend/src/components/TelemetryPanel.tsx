import {
  Box,
  Card,
  CardContent,
  Chip,
  Divider,
  Grid,
  Stack,
  Typography,
} from '@mui/material';
import type { TelemetryState } from '../types/api';

type Props = {
  telemetry: TelemetryState;
};

function fmtNumber(value: number | null | undefined, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return '-';
  }
  return value.toFixed(digits);
}

function fmtBool(value: boolean | null) {
  if (value === null) {
    return 'unknown';
  }
  return value ? 'yes' : 'no';
}

function Metric({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <Stack
      spacing={0.35}
      sx={{
        p: 1.25,
        borderRadius: 3,
        background: 'rgba(255,255,255,0.025)',
        border: '1px solid rgba(255,255,255,0.04)',
        minHeight: 78,
      }}
    >
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2" fontWeight={700}>
        {value}
      </Typography>
    </Stack>
  );
}

function PhaseLamp({
  label,
  value,
}: {
  label: string;
  value: number | null;
}) {
  const on = value === 1;

  return (
    <Stack
      spacing={0.75}
      alignItems="center"
      sx={{
        p: 1.25,
        borderRadius: 3,
        background: 'rgba(255,255,255,0.025)',
        border: '1px solid rgba(255,255,255,0.04)',
      }}
    >
      <Box
        sx={{
          width: 18,
          height: 18,
          borderRadius: '50%',
          bgcolor: on ? '#60d394' : 'rgba(255,255,255,0.16)',
          boxShadow: on ? '0 0 20px rgba(96,211,148,0.55)' : 'none',
        }}
      />
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2" fontWeight={700}>
        {value ?? '-'}
      </Typography>
    </Stack>
  );
}

export function TelemetryPanel({ telemetry }: Props) {
  const { system, mpu, stepper, i2c, wifi, driver } = telemetry;

  return (
    <Card sx={{ borderRadius: 5 }}>
      <CardContent>
        <Stack spacing={2.25}>
          <Stack
            direction={{ xs: 'column', lg: 'row' }}
            spacing={1.25}
            justifyContent="space-between"
            alignItems={{ xs: 'flex-start', lg: 'center' }}
          >
            <Stack spacing={0.5}>
              <Typography variant="h6">MCU telemetry deck</Typography>
              <Typography variant="body2" color="text.secondary">
                Parsed runtime state from firmware, serial link, sensors, and driver logic.
              </Typography>
            </Stack>

            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              <Chip
                label={mpu.ready ? 'MPU ready' : mpu.ready === false ? 'MPU error' : 'MPU waiting'}
                color={mpu.ready ? 'success' : mpu.ready === false ? 'error' : 'default'}
              />
              <Chip
                label={driver.serialConnected ? 'Serial live' : 'Serial offline'}
                color={driver.serialConnected ? 'success' : 'default'}
              />
              <Chip
                label={driver.toolingRunning ? `Tooling ${driver.toolingAction}` : 'Tooling idle'}
                color={driver.toolingRunning ? 'warning' : 'default'}
              />
            </Stack>
          </Stack>

          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 6 }}>
              <Stack spacing={1.25}>
                <Typography variant="subtitle1">Runtime</Typography>
                <Grid container spacing={1.25}>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Uptime" value={system.uptimeMs !== null ? `${Math.round(system.uptimeMs / 1000)} s` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Tick" value={system.tick !== null ? String(system.tick) : '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Tick delay" value={system.tickDelayMs !== null ? `${system.tickDelayMs} ms` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 6 }}>
                    <Metric label="Firmware" value={system.firmware ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 6 }}>
                    <Metric label="App mode" value={system.appMode ?? '-'} />
                  </Grid>
                </Grid>
                {system.lastError ? (
                  <Typography variant="body2" color="warning.main">
                    runtime error: {system.lastError}
                  </Typography>
                ) : null}
              </Stack>
            </Grid>

            <Grid size={{ xs: 12, md: 6 }}>
              <Stack spacing={1.25}>
                <Typography variant="subtitle1">Serial and tooling</Typography>
                <Grid container spacing={1.25}>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Port" value={driver.serialPort ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Baud" value={driver.baudRate !== null ? String(driver.baudRate) : '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Flashing port" value={driver.toolingPort ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Tool action" value={driver.toolingAction ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Last exit" value={driver.lastToolExitCode !== null ? String(driver.lastToolExitCode) : '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Serial connected" value={fmtBool(driver.serialConnected)} />
                  </Grid>
                </Grid>
                {driver.toolingError ? (
                  <Typography variant="body2" color="warning.main">
                    tooling error: {driver.toolingError}
                  </Typography>
                ) : null}
              </Stack>
            </Grid>
          </Grid>

          <Divider />

          <Grid container spacing={2}>
            <Grid size={{ xs: 12, lg: 6 }}>
              <Stack spacing={1.25}>
                <Typography variant="subtitle1">MPU / IMU</Typography>
                <Grid container spacing={1.25}>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Metric label="Address" value={mpu.address ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Metric label="WHO_AM_I" value={mpu.whoAmI ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Metric label="Model" value={mpu.model ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Metric label="Temp" value={mpu.tempC !== null ? `${fmtNumber(mpu.tempC)} C` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 4, sm: 4 }}>
                    <Metric label="Accel X" value={mpu.accel.x !== null ? `${fmtNumber(mpu.accel.x, 3)} g` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 4, sm: 4 }}>
                    <Metric label="Accel Y" value={mpu.accel.y !== null ? `${fmtNumber(mpu.accel.y, 3)} g` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 4, sm: 4 }}>
                    <Metric label="Accel Z" value={mpu.accel.z !== null ? `${fmtNumber(mpu.accel.z, 3)} g` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 4, sm: 4 }}>
                    <Metric label="Gyro X" value={mpu.gyro.x !== null ? `${fmtNumber(mpu.gyro.x)} dps` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 4, sm: 4 }}>
                    <Metric label="Gyro Y" value={mpu.gyro.y !== null ? `${fmtNumber(mpu.gyro.y)} dps` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 4, sm: 4 }}>
                    <Metric label="Gyro Z" value={mpu.gyro.z !== null ? `${fmtNumber(mpu.gyro.z)} dps` : '-'} />
                  </Grid>
                </Grid>
                {mpu.error ? (
                  <Typography variant="body2" color="warning.main">
                    mpu error: {mpu.error}
                  </Typography>
                ) : null}
              </Stack>
            </Grid>

            <Grid size={{ xs: 12, lg: 6 }}>
              <Stack spacing={1.25}>
                <Typography variant="subtitle1">Stepper / driver</Typography>
                <Grid container spacing={1.25}>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Mode" value={stepper.mode ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Sweep" value={stepper.sweepState ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Last cmd" value={stepper.lastCommand ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Delay" value={stepper.delayMs !== null ? `${stepper.delayMs} ms` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Speed" value={stepper.stepsPerSecond !== null ? `${fmtNumber(stepper.stepsPerSecond)} step/s` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Phase" value={stepper.phaseIndex !== null ? String(stepper.phaseIndex) : '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Total steps" value={stepper.totalSteps !== null ? String(stepper.totalSteps) : '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Coils" value={fmtBool(stepper.coilsEnabled)} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="UART ready" value={fmtBool(stepper.uartReady)} />
                  </Grid>
                </Grid>

                <Grid container spacing={1.25}>
                  <Grid size={{ xs: 3, sm: 3 }}>
                    <PhaseLamp label="IN1" value={stepper.pins.in1} />
                  </Grid>
                  <Grid size={{ xs: 3, sm: 3 }}>
                    <PhaseLamp label="IN2" value={stepper.pins.in2} />
                  </Grid>
                  <Grid size={{ xs: 3, sm: 3 }}>
                    <PhaseLamp label="IN3" value={stepper.pins.in3} />
                  </Grid>
                  <Grid size={{ xs: 3, sm: 3 }}>
                    <PhaseLamp label="IN4" value={stepper.pins.in4} />
                  </Grid>
                </Grid>
              </Stack>
            </Grid>
          </Grid>

          <Divider />

          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 6 }}>
              <Stack spacing={1.25}>
                <Typography variant="subtitle1">I2C bus</Typography>
                <Grid container spacing={1.25}>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="Ready" value={fmtBool(i2c.ready)} />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="MPU addr" value={i2c.detectedMpuAddress ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    <Metric label="Devices" value={i2c.devices.length > 0 ? i2c.devices.join(', ') : '-'} />
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    <Metric label="Scan summary" value={i2c.lastScanSummary ?? '-'} />
                  </Grid>
                </Grid>
                {i2c.error ? (
                  <Typography variant="body2" color="warning.main">
                    i2c error: {i2c.error}
                  </Typography>
                ) : null}
              </Stack>
            </Grid>

            <Grid size={{ xs: 12, md: 6 }}>
              <Stack spacing={1.25}>
                <Typography variant="subtitle1">Wi-Fi</Typography>
                <Grid container spacing={1.25}>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="Enabled" value={fmtBool(wifi.enabled)} />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="Connected" value={fmtBool(wifi.connected)} />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="SSID" value={wifi.ssid ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="IP" value={wifi.ip ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    <Metric label="MAC" value={wifi.mac ?? '-'} />
                  </Grid>
                </Grid>
                {wifi.lastError ? (
                  <Typography variant="body2" color="warning.main">
                    wifi error: {wifi.lastError}
                  </Typography>
                ) : null}
              </Stack>
            </Grid>
          </Grid>
        </Stack>
      </CardContent>
    </Card>
  );
}