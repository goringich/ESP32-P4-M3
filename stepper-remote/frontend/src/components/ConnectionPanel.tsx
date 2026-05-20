import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  FormHelperText,
  MenuItem,
  Stack,
  ToggleButton,
  ToggleButtonGroup,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import {
  connectPort,
  disconnectPort,
  fetchPorts,
  updateTransport,
} from '../api/client';
import type {
  ConnectionState,
  PortInfo,
  TransportMode,
  TransportState,
} from '../types/api';

type Props = {
  connection: ConnectionState;
  transport: TransportState;
  onConnectionChange: (state: ConnectionState) => void;
  onTransportChange: (state: TransportState) => void;
};

export function ConnectionPanel({
  connection,
  transport,
  onConnectionChange,
  onTransportChange,
}: Props) {
  const [ports, setPorts] = useState<PortInfo[]>([]);
  const [path, setPath] = useState('');
  const [baudRate, setBaudRate] = useState('115200');
  const [wifiBaseUrl, setWifiBaseUrl] = useState(transport.wifiBaseUrl);
  const [loadingPorts, setLoadingPorts] = useState(false);
  const [portError, setPortError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const selectedPort = useMemo(
    () => ports.find((item) => item.path === path) ?? null,
    [ports, path]
  );

  const loadPorts = async () => {
    setLoadingPorts(true);
    setPortError(null);

    try {
      const data = await fetchPorts();
      setPorts(data);

      if (!path && data.length > 0) {
        setPath(data[0].path);
      }

      if (data.length === 0) {
        setPortError('UART-порты не найдены. Подключите плату и обновите список.');
      }
    } catch (error) {
      setPortError(error instanceof Error ? error.message : 'Не удалось загрузить список UART-портов');
    } finally {
      setLoadingPorts(false);
    }
  };

  useEffect(() => {
    loadPorts().catch(() => {});
  }, []);

  useEffect(() => {
    setWifiBaseUrl(transport.wifiBaseUrl);
  }, [transport.wifiBaseUrl]);

  const switchTransport = async (mode: TransportMode) => {
    setBusy(true);
    setPortError(null);

    try {
      const next = await updateTransport(mode, wifiBaseUrl);
      onTransportChange(next);
    } catch (error) {
      setPortError(error instanceof Error ? error.message : 'Не удалось переключить транспорт');
    } finally {
      setBusy(false);
    }
  };

  const handleConnect = async () => {
    setBusy(true);
    setPortError(null);

    try {
      await connectPort(path, Number(baudRate));
      onConnectionChange({
        isOpen: true,
        path,
        baudRate: Number(baudRate),
      });
    } catch (error) {
      setPortError(error instanceof Error ? error.message : 'Не удалось подключиться');
    } finally {
      setBusy(false);
    }
  };

  const handleDisconnect = async () => {
    setBusy(true);
    setPortError(null);

    try {
      await disconnectPort();
      onConnectionChange({
        isOpen: false,
        path: null,
        baudRate: null,
      });
    } catch (error) {
      setPortError(error instanceof Error ? error.message : 'Не удалось отключиться');
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Stack spacing={2.25}>
          <Stack spacing={0.5}>
            <Typography variant="h6">Подключение</Typography>
            <Typography variant="body2" color="text.secondary">
              Wi-Fi и UART здесь работают параллельно. Wi-Fi задаёт основной канал
              команд и телеметрии, а UART остаётся для питания, логов и аварийного отката.
            </Typography>
          </Stack>

          <ToggleButtonGroup
            exclusive
            value={transport.mode}
            onChange={(_event, value: TransportMode | null) => {
              if (value) {
                void switchTransport(value);
              }
            }}
            size="small"
            color="primary"
          >
            <ToggleButton value="wifi">Wi-Fi в приоритете</ToggleButton>
            <ToggleButton value="serial">Форсировать UART</ToggleButton>
          </ToggleButtonGroup>

          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            <Chip label={`режим ${transport.mode === 'wifi' ? 'wifi-first' : 'uart-only'}`} color={transport.mode === 'wifi' ? 'secondary' : 'primary'} />
            <Chip
              label={
                transport.wifiConnected
                  ? 'Wi-Fi мост активен'
                  : 'Wi-Fi мост не поднят'
              }
              color={
                transport.wifiConnected
                  ? 'success'
                  : 'default'
              }
            />
            <Chip label={connection.isOpen ? 'UART открыт' : 'UART закрыт'} color={connection.isOpen ? 'success' : 'default'} />
            <Chip label={loadingPorts ? 'поиск портов' : `${ports.length} порт${ports.length === 1 ? '' : 'ов'}`} />
            <Chip label={`baud ${baudRate}`} color="info" />
          </Stack>

          <Alert severity="info" variant="outlined">
            Эта сборка поддерживает только `UART` и `Wi-Fi` transport. Bluetooth в текущем
            `ESP32-P4 + ESP-Hosted` контуре не выведен как рабочий канал, поэтому отдельный
            переключатель Bluetooth здесь не добавлялся.
          </Alert>

          <Alert severity="info" variant="outlined">
            В режиме `Wi-Fi` браузер не ходит на плату напрямую. Запросы идут в backend на
            `:3001`, а backend уже проксирует их в `http://192.168.4.1`. Поэтому устройство с UI
            может оставаться в другом Wi-Fi, но backend-хост обязан реально видеть ESP AP.
          </Alert>

          {transport.lastError ? (
            <Alert severity="warning" variant="outlined">
              Ошибка Wi-Fi транспорта: {transport.lastError}
            </Alert>
          ) : null}

          {portError ? (
            <Alert severity={ports.length === 0 ? 'info' : 'error'} variant="outlined">
              {portError}
            </Alert>
          ) : null}

          <TextField
            label="URL Wi-Fi API платы"
            value={wifiBaseUrl}
            onChange={(event) => setWifiBaseUrl(event.target.value)}
            fullWidth
            placeholder="http://192.168.4.1"
          />

          {ports.length > 0 ? (
            <TextField
              select
              label="Порт"
              value={path}
              onChange={(event) => setPath(event.target.value)}
              fullWidth
            >
              {ports.map((port) => (
                <MenuItem key={port.path} value={port.path}>
                  {port.friendlyName}
                </MenuItem>
              ))}
            </TextField>
          ) : (
            <TextField
              label="Путь к порту"
              value={path}
              onChange={(event) => setPath(event.target.value)}
              fullWidth
              placeholder="/dev/ttyUSB0"
            />
          )}

          {ports.length === 0 ? (
            <FormHelperText sx={{ mt: -1 }}>
              {loadingPorts
                ? 'Идёт поиск UART-портов...'
                : 'Порты не найдены. Если знаете путь, введите его вручную.'}
            </FormHelperText>
          ) : null}

          <TextField
            label="Скорость UART"
            value={baudRate}
            onChange={(event) => setBaudRate(event.target.value)}
            fullWidth
          />

          <FormHelperText sx={{ mt: -1 }}>
            Wi-Fi должен смотреть в `http://192.168.4.1`, а UART можно держать открытым параллельно.
          </FormHelperText>

          {selectedPort ? (
            <Box
              sx={{
                p: 1.5,
                borderRadius: 3,
                border: '1px solid rgba(255,255,255,0.06)',
                background: 'rgba(255,255,255,0.025)',
              }}
            >
              <Stack spacing={0.75}>
                <Typography variant="subtitle2">Данные порта</Typography>
                <Typography variant="body2" color="text.secondary">
                  путь: {selectedPort.path}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  vendor: {selectedPort.vendorId || '-'} / product: {selectedPort.productId || '-'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  устройство: {selectedPort.manufacturer || '-'}
                </Typography>
              </Stack>
            </Box>
          ) : null}

          <Box
            sx={{
              p: 1.5,
              borderRadius: 3,
              border: '1px solid rgba(99,230,255,0.14)',
              background:
                'linear-gradient(180deg, rgba(99,230,255,0.08), rgba(255,255,255,0.02))',
            }}
          >
            <Stack spacing={0.75}>
              <Typography variant="subtitle2">Порядок работы</Typography>
              <Typography variant="body2" color="text.secondary">
                1. Держите Wi-Fi в приоритете, чтобы команды шли на плату по `192.168.4.1`.
              </Typography>
              <Typography variant="body2" color="text.secondary">
                2. Оставляйте UART открытым для логов, питания и аварийного фоллбэка.
              </Typography>
              <Typography variant="body2" color="text.secondary">
                3. Если Wi-Fi мост упал, backend сам вернёт команду в UART, если порт открыт.
              </Typography>
            </Stack>
          </Box>

          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            <Button
              variant="contained"
              onClick={() => {
                void switchTransport('wifi');
              }}
              disabled={!wifiBaseUrl.trim() || busy}
            >
              {busy && transport.mode === 'wifi' ? 'Применение...' : 'Wi-Fi в приоритете'}
            </Button>

            <Button
              variant="outlined"
              color={transport.mode === 'serial' ? 'warning' : 'inherit'}
              onClick={() => {
                void switchTransport('serial');
              }}
              disabled={busy}
            >
              Форсировать UART
            </Button>

            <Button
              variant="contained"
              onClick={handleConnect}
              disabled={!path || busy}
            >
              {busy && !connection.isOpen ? 'Подключение...' : 'Открыть UART'}
            </Button>

            <Button variant="outlined" onClick={loadPorts} disabled={busy}>
              {loadingPorts ? 'Обновление...' : 'Обновить порты'}
            </Button>

            <Button variant="outlined" color="error" onClick={handleDisconnect} disabled={busy || !connection.isOpen}>
              {busy && connection.isOpen ? 'Закрытие...' : 'Закрыть UART'}
            </Button>
          </Stack>

          <Box
            sx={{
              p: 1.5,
              borderRadius: 3,
              border: '1px solid rgba(255,255,255,0.06)',
              background: 'rgba(255,255,255,0.025)',
            }}
          >
            <Stack spacing={0.75}>
              <Typography variant="subtitle2">Состояние каналов</Typography>
              <Typography variant="body2" color="text.secondary">
                Wi-Fi URL: {transport.wifiBaseUrl}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Wi-Fi: {transport.wifiConnected ? 'API платы доступен' : 'ожидание API платы'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                последняя телеметрия Wi-Fi: {transport.lastTelemetryAt ? new Date(transport.lastTelemetryAt).toLocaleTimeString() : '-'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                UART: {connection.isOpen ? `${connection.path} @ ${connection.baudRate}` : 'закрыт'}
              </Typography>
            </Stack>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}
