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
    return 'неизвестно';
  }
  return value ? 'да' : 'нет';
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
  const { system, mpu, stepper, i2c, wifi, ble, driver } = telemetry;

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
              <Typography variant="h6">Телеметрия платы</Typography>
              <Typography variant="body2" color="text.secondary">
                Здесь показано текущее состояние прошивки, датчика, Wi-Fi, UART и привода.
              </Typography>
            </Stack>

            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              <Chip
                label={mpu.ready ? 'MPU готов' : mpu.ready === false ? 'MPU ошибка' : 'MPU ожидание'}
                color={mpu.ready ? 'success' : mpu.ready === false ? 'error' : 'default'}
              />
              <Chip
                label={driver.serialConnected ? 'UART активен' : 'UART не активен'}
                color={driver.serialConnected ? 'success' : 'default'}
              />
              <Chip
                label={driver.toolingRunning ? `Задача ${driver.toolingAction}` : 'Задач нет'}
                color={driver.toolingRunning ? 'warning' : 'default'}
              />
            </Stack>
          </Stack>

          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 6 }}>
              <Stack spacing={1.25}>
                <Typography variant="subtitle1">Общее состояние</Typography>
                <Grid container spacing={1.25}>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Время работы" value={system.uptimeMs !== null ? `${Math.round(system.uptimeMs / 1000)} c` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Тик" value={system.tick !== null ? String(system.tick) : '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Задержка тика" value={system.tickDelayMs !== null ? `${system.tickDelayMs} ms` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 6 }}>
                    <Metric label="Прошивка" value={system.firmware ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 6 }}>
                    <Metric label="Режим приложения" value={system.appMode ?? '-'} />
                  </Grid>
                </Grid>
                {system.lastError ? (
                  <Typography variant="body2" color="warning.main">
                    ошибка runtime: {system.lastError}
                  </Typography>
                ) : null}
              </Stack>
            </Grid>

            <Grid size={{ xs: 12, md: 6 }}>
              <Stack spacing={1.25}>
                <Typography variant="subtitle1">UART и задачи</Typography>
                <Grid container spacing={1.25}>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Порт" value={driver.serialPort ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Скорость" value={driver.baudRate !== null ? String(driver.baudRate) : '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Порт прошивки" value={driver.toolingPort ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Текущая задача" value={driver.toolingAction ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Последний код" value={driver.lastToolExitCode !== null ? String(driver.lastToolExitCode) : '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="UART подключен" value={fmtBool(driver.serialConnected)} />
                  </Grid>
                </Grid>
                {driver.toolingError ? (
                  <Typography variant="body2" color="warning.main">
                    ошибка задачи: {driver.toolingError}
                  </Typography>
                ) : null}
              </Stack>
            </Grid>
          </Grid>

          <Divider />

          <Grid container spacing={2}>
            <Grid size={{ xs: 12, lg: 6 }}>
              <Stack spacing={1.25}>
                <Typography variant="subtitle1">IMU / MPU</Typography>
                <Grid container spacing={1.25}>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Metric label="Адрес" value={mpu.address ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Metric label="WHO_AM_I" value={mpu.whoAmI ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Metric label="Модель" value={mpu.model ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 3 }}>
                    <Metric label="Температура" value={mpu.tempC !== null ? `${fmtNumber(mpu.tempC)} C` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 4, sm: 4 }}>
                    <Metric label="Ускорение X" value={mpu.accel.x !== null ? `${fmtNumber(mpu.accel.x, 3)} g` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 4, sm: 4 }}>
                    <Metric label="Ускорение Y" value={mpu.accel.y !== null ? `${fmtNumber(mpu.accel.y, 3)} g` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 4, sm: 4 }}>
                    <Metric label="Ускорение Z" value={mpu.accel.z !== null ? `${fmtNumber(mpu.accel.z, 3)} g` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 4, sm: 4 }}>
                    <Metric label="Гироскоп X" value={mpu.gyro.x !== null ? `${fmtNumber(mpu.gyro.x)} dps` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 4, sm: 4 }}>
                    <Metric label="Гироскоп Y" value={mpu.gyro.y !== null ? `${fmtNumber(mpu.gyro.y)} dps` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 4, sm: 4 }}>
                    <Metric label="Гироскоп Z" value={mpu.gyro.z !== null ? `${fmtNumber(mpu.gyro.z)} dps` : '-'} />
                  </Grid>
                </Grid>
                {mpu.error ? (
                  <Typography variant="body2" color="warning.main">
                    ошибка MPU: {mpu.error}
                  </Typography>
                ) : null}
              </Stack>
            </Grid>

            <Grid size={{ xs: 12, lg: 6 }}>
              <Stack spacing={1.25}>
                <Typography variant="subtitle1">Привод</Typography>
                <Grid container spacing={1.25}>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Режим" value={stepper.mode ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Качание" value={stepper.sweepState ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Последняя команда" value={stepper.lastCommand ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Задержка" value={stepper.delayMs !== null ? `${stepper.delayMs} ms` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Скорость" value={stepper.stepsPerSecond !== null ? `${fmtNumber(stepper.stepsPerSecond)} шаг/с` : '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Фаза" value={stepper.phaseIndex !== null ? String(stepper.phaseIndex) : '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Всего шагов" value={stepper.totalSteps !== null ? String(stepper.totalSteps) : '-'} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="Катушки" value={fmtBool(stepper.coilsEnabled)} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <Metric label="UART готов" value={fmtBool(stepper.uartReady)} />
                  </Grid>
                </Grid>

                <Grid container spacing={1.25}>
                  <Grid size={{ xs: 3, sm: 3 }}>
                    <PhaseLamp
                      label={`IN1 / GPIO ${stepper.gpioPins.in1 ?? '-'}`}
                      value={stepper.pins.in1}
                    />
                  </Grid>
                  <Grid size={{ xs: 3, sm: 3 }}>
                    <PhaseLamp
                      label={`IN2 / GPIO ${stepper.gpioPins.in2 ?? '-'}`}
                      value={stepper.pins.in2}
                    />
                  </Grid>
                  <Grid size={{ xs: 3, sm: 3 }}>
                    <PhaseLamp
                      label={`IN3 / GPIO ${stepper.gpioPins.in3 ?? '-'}`}
                      value={stepper.pins.in3}
                    />
                  </Grid>
                  <Grid size={{ xs: 3, sm: 3 }}>
                    <PhaseLamp
                      label={`IN4 / GPIO ${stepper.gpioPins.in4 ?? '-'}`}
                      value={stepper.pins.in4}
                    />
                  </Grid>
                </Grid>
              </Stack>
            </Grid>
          </Grid>

          <Divider />

          <Grid container spacing={2}>
            <Grid size={{ xs: 12, md: 6 }}>
              <Stack spacing={1.25}>
                <Typography variant="subtitle1">Шина I2C</Typography>
                <Grid container spacing={1.25}>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="Готовность" value={fmtBool(i2c.ready)} />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="Адрес MPU" value={i2c.detectedMpuAddress ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    <Metric label="Устройства" value={i2c.devices.length > 0 ? i2c.devices.join(', ') : '-'} />
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    <Metric label="Итог сканирования" value={i2c.lastScanSummary ?? '-'} />
                  </Grid>
                </Grid>
                {i2c.error ? (
                  <Typography variant="body2" color="warning.main">
                    ошибка I2C: {i2c.error}
                  </Typography>
                ) : null}
              </Stack>
            </Grid>

            <Grid size={{ xs: 12, md: 6 }}>
              <Stack spacing={1.25}>
                <Typography variant="subtitle1">Wi-Fi</Typography>
                <Grid container spacing={1.25}>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="Включен" value={fmtBool(wifi.enabled)} />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="Подключен" value={fmtBool(wifi.connected)} />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="SSID" value={wifi.ssid ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="IP" value={wifi.ip ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="AP запущен" value={fmtBool(wifi.apStarted ?? null)} />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="STA подключен" value={fmtBool(wifi.staConnected ?? null)} />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="AP SSID" value={wifi.apSsid ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="AP IP" value={wifi.apIp ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="STA IP" value={wifi.staIp ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="MAC" value={wifi.mac ?? '-'} />
                  </Grid>
                </Grid>
                {wifi.lastError ? (
                  <Typography variant="body2" color="warning.main">
                    ошибка Wi-Fi: {wifi.lastError}
                  </Typography>
                ) : null}
              </Stack>
            </Grid>

            <Grid size={{ xs: 12, md: 6 }}>
              <Stack spacing={1.25}>
                <Typography variant="subtitle1">Bluetooth LE</Typography>
                <Grid container spacing={1.25}>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="Инициализирован" value={fmtBool(ble.initialized)} />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="Контроллер включен" value={fmtBool(ble.controllerEnabled)} />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="Реклама" value={fmtBool(ble.advertising)} />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="Подключение" value={fmtBool(ble.connected)} />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="Notify" value={fmtBool(ble.notifyEnabled)} />
                  </Grid>
                  <Grid size={{ xs: 6 }}>
                    <Metric label="Имя" value={ble.deviceName ?? '-'} />
                  </Grid>
                  <Grid size={{ xs: 12 }}>
                    <Metric label="BT-адрес" value={ble.address ?? '-'} />
                  </Grid>
                </Grid>
                {ble.lastError ? (
                  <Typography variant="body2" color="warning.main">
                    ошибка BLE: {ble.lastError}
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
