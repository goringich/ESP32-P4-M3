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
        setPortError('No serial ports detected. Connect the ESP board and refresh the list.');
      }
    } catch (error) {
      setPortError(error instanceof Error ? error.message : 'Unable to load serial ports');
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
      setPortError(error instanceof Error ? error.message : 'Unable to switch transport');
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
      setPortError(error instanceof Error ? error.message : 'Unable to connect');
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
      setPortError(error instanceof Error ? error.message : 'Unable to disconnect');
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Stack spacing={2.25}>
          <Stack spacing={0.5}>
            <Typography variant="h6">Transport gateway</Typography>
            <Typography variant="body2" color="text.secondary">
              Run the dashboard either over direct UART or through the MCU Wi-Fi API when the board is on battery power.
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
            <ToggleButton value="serial">Serial</ToggleButton>
            <ToggleButton value="wifi">Wi-Fi</ToggleButton>
          </ToggleButtonGroup>

          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            <Chip label={`mode ${transport.mode}`} color={transport.mode === 'wifi' ? 'secondary' : 'primary'} />
            <Chip
              label={
                transport.mode === 'wifi'
                  ? transport.wifiConnected
                    ? 'wifi bridge live'
                    : 'wifi bridge idle'
                  : connection.isOpen
                    ? 'link open'
                    : 'link closed'
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
            <Chip label={loadingPorts ? 'scanning ports' : `${ports.length} port${ports.length === 1 ? '' : 's'}`} />
            <Chip label={`baud ${baudRate}`} color="info" />
          </Stack>

          {portError ? (
            <Alert severity={ports.length === 0 ? 'info' : 'error'} variant="outlined">
              {portError}
            </Alert>
          ) : null}

          {transport.mode === 'wifi' ? (
            <TextField
              label="MCU Wi-Fi URL"
              value={wifiBaseUrl}
              onChange={(event) => setWifiBaseUrl(event.target.value)}
              fullWidth
              placeholder="http://192.168.4.1"
            />
          ) : ports.length > 0 ? (
            <TextField
              select
              label="Port"
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
              label="Port path"
              value={path}
              onChange={(event) => setPath(event.target.value)}
              fullWidth
              placeholder="/dev/ttyUSB0"
            />
          )}

          {transport.mode === 'serial' && ports.length === 0 ? (
            <FormHelperText sx={{ mt: -1 }}>
              {loadingPorts
                ? 'Scanning for ports...'
                : 'No ports detected. Enter the path manually if you know it.'}
            </FormHelperText>
          ) : null}

          {transport.mode === 'serial' ? (
            <TextField
              label="Baud rate"
              value={baudRate}
              onChange={(event) => setBaudRate(event.target.value)}
              fullWidth
            />
          ) : (
            <FormHelperText sx={{ mt: -1 }}>
              Connect the computer to the ESP Wi-Fi network, then point this URL to the board API.
            </FormHelperText>
          )}

          {transport.mode === 'serial' && selectedPort ? (
            <Box
              sx={{
                p: 1.5,
                border: '1px solid rgba(255,255,255,0.06)',
                background: 'rgba(255,255,255,0.025)',
              }}
            >
              <Stack spacing={0.75}>
                <Typography variant="subtitle2">Port details</Typography>
                <Typography variant="body2" color="text.secondary">
                  path: {selectedPort.path}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  vendor: {selectedPort.vendorId || '-'} / product: {selectedPort.productId || '-'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  manufacturer: {selectedPort.manufacturer || '-'}
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
                  ? 'Switching...'
                  : 'Activate Wi-Fi bridge'
                : busy && !connection.isOpen
                  ? 'Connecting...'
                  : 'Connect'}
            </Button>

            {transport.mode === 'serial' ? (
              <Button variant="outlined" onClick={loadPorts} disabled={busy}>
                {loadingPorts ? 'Refreshing...' : 'Refresh'}
              </Button>
            ) : null}

            <Button variant="outlined" color="error" onClick={handleDisconnect} disabled={busy}>
              {transport.mode === 'wifi'
                ? busy
                  ? 'Releasing...'
                  : 'Return to serial'
                : busy && connection.isOpen
                  ? 'Closing...'
                  : 'Disconnect'}
            </Button>
          </Stack>

          {transport.mode === 'wifi' ? (
            <Box
              sx={{
                p: 1.5,
                border: '1px solid rgba(255,255,255,0.06)',
                background: 'rgba(255,255,255,0.025)',
              }}
            >
              <Stack spacing={0.75}>
                <Typography variant="subtitle2">Wi-Fi bridge details</Typography>
                <Typography variant="body2" color="text.secondary">
                  base URL: {transport.wifiBaseUrl}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  last telemetry: {transport.lastTelemetryAt ? new Date(transport.lastTelemetryAt).toLocaleTimeString() : '-'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  state: {transport.wifiConnected ? 'connected to MCU API' : 'waiting for MCU API'}
                </Typography>
              </Stack>
            </Box>
          ) : null}
        </Stack>
      </CardContent>
    </Card>
  );
}
