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
      if (transport.mode === 'wifi') {
        const next = await updateTransport('wifi', wifiBaseUrl);
        onTransportChange(next);
        return;
      }

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
      if (transport.mode === 'wifi') {
        const next = await updateTransport('serial', wifiBaseUrl);
        onTransportChange(next);
        return;
      }

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
              Здесь выбирается канал связи с платой. Питание может оставаться по USB/UART,
              а команды и телеметрия могут идти через Wi-Fi API платы.
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
            <ToggleButton value="serial">UART</ToggleButton>
            <ToggleButton value="wifi">Wi-Fi</ToggleButton>
          </ToggleButtonGroup>

          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            <Chip label={`режим ${transport.mode === 'wifi' ? 'wifi' : 'uart'}`} color={transport.mode === 'wifi' ? 'secondary' : 'primary'} />
            <Chip
              label={
                transport.mode === 'wifi'
                  ? transport.wifiConnected
                    ? 'Wi-Fi мост активен'
                    : 'Wi-Fi мост не поднят'
                  : connection.isOpen
                    ? 'порт открыт'
                    : 'порт закрыт'
              }
              color={
                transport.mode === 'wifi'
                  ? transport.wifiConnected
                    ? 'success'
                    : 'default'
                  : connection.isOpen
                    ? 'success'
                    : 'default'
              }
            />
            <Chip label={loadingPorts ? 'поиск портов' : `${ports.length} порт${ports.length === 1 ? '' : 'ов'}`} />
            <Chip label={`baud ${baudRate}`} color="info" />
          </Stack>

          <Alert severity="info" variant="outlined">
            Эта сборка поддерживает только `UART` и `Wi-Fi` transport. Bluetooth в текущем
            `ESP32-P4 + ESP-Hosted` контуре не выведен как рабочий канал, поэтому отдельный
            переключатель Bluetooth здесь не добавлялся.
          </Alert>

          {transport.mode === 'wifi' && transport.lastError ? (
            <Alert severity="warning" variant="outlined">
              Ошибка Wi-Fi транспорта: {transport.lastError}
            </Alert>
          ) : null}

          {portError ? (
            <Alert severity={ports.length === 0 ? 'info' : 'error'} variant="outlined">
              {portError}
            </Alert>
          ) : null}

          {transport.mode === 'wifi' ? (
            <TextField
              label="URL Wi-Fi API платы"
              value={wifiBaseUrl}
              onChange={(event) => setWifiBaseUrl(event.target.value)}
              fullWidth
              placeholder="http://192.168.4.1"
            />
          ) : ports.length > 0 ? (
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

          {transport.mode === 'serial' && ports.length === 0 ? (
            <FormHelperText sx={{ mt: -1 }}>
              {loadingPorts
                ? 'Идёт поиск UART-портов...'
                : 'Порты не найдены. Если знаете путь, введите его вручную.'}
            </FormHelperText>
          ) : null}

          {transport.mode === 'serial' ? (
            <TextField
              label="Скорость UART"
              value={baudRate}
              onChange={(event) => setBaudRate(event.target.value)}
              fullWidth
            />
          ) : (
            <FormHelperText sx={{ mt: -1 }}>
              Подключите компьютер к сети ESP и укажите адрес API платы.
            </FormHelperText>
          )}

          {transport.mode === 'serial' && selectedPort ? (
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

          {transport.mode === 'wifi' ? (
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
                <Typography variant="subtitle2">Порядок работы по Wi-Fi</Typography>
                <Typography variant="body2" color="text.secondary">
                  1. Оставьте USB/UART для питания и логов, если это нужно.
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  2. Подключитесь к Wi-Fi сети платы и укажите URL её API.
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  3. Активируйте Wi-Fi мост и убедитесь, что телеметрия пошла до отправки команд.
                </Typography>
              </Stack>
            </Box>
          ) : null}

          <Stack direction="row" spacing={1}>
            <Button
              variant="contained"
              onClick={handleConnect}
              disabled={(transport.mode === 'serial' ? !path : !wifiBaseUrl.trim()) || busy}
              sx={{ flex: 1 }}
            >
              {transport.mode === 'wifi'
                ? busy
                  ? 'Переключение...'
                  : 'Включить Wi-Fi мост'
                : busy && !connection.isOpen
                  ? 'Подключение...'
                  : 'Подключить'}
            </Button>

            {transport.mode === 'serial' ? (
              <Button variant="outlined" onClick={loadPorts} disabled={busy}>
                {loadingPorts ? 'Обновление...' : 'Обновить'}
              </Button>
            ) : null}

            <Button variant="outlined" color="error" onClick={handleDisconnect} disabled={busy}>
              {transport.mode === 'wifi'
                ? busy
                  ? 'Отключение...'
                  : 'Вернуться на UART'
                : busy && connection.isOpen
                  ? 'Закрытие...'
                  : 'Отключить'}
            </Button>
          </Stack>

          {transport.mode === 'wifi' ? (
            <Box
              sx={{
                p: 1.5,
                borderRadius: 3,
                border: '1px solid rgba(255,255,255,0.06)',
                background: 'rgba(255,255,255,0.025)',
              }}
            >
              <Stack spacing={0.75}>
                <Typography variant="subtitle2">Состояние Wi-Fi моста</Typography>
                <Typography variant="body2" color="text.secondary">
                  URL: {transport.wifiBaseUrl}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  последняя телеметрия: {transport.lastTelemetryAt ? new Date(transport.lastTelemetryAt).toLocaleTimeString() : '-'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  состояние: {transport.wifiConnected ? 'API платы доступен' : 'ожидание API платы'}
                </Typography>
              </Stack>
            </Box>
          ) : null}
        </Stack>
      </CardContent>
    </Card>
  );
}
