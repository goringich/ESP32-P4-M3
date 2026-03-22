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
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useMemo, useState } from 'react';
import { connectPort, disconnectPort, fetchPorts } from '../api/client';
import type { ConnectionState, PortInfo } from '../types/api';

type Props = {
  connection: ConnectionState;
  onConnectionChange: (state: ConnectionState) => void;
};

export function ConnectionPanel({ connection, onConnectionChange }: Props) {
  const [ports, setPorts] = useState<PortInfo[]>([]);
  const [path, setPath] = useState('');
  const [baudRate, setBaudRate] = useState('115200');
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
      setPortError(error instanceof Error ? error.message : 'Unable to connect');
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
            <Typography variant="h6">Serial gateway</Typography>
            <Typography variant="body2" color="text.secondary">
              Select the board port, open the UART stream, and route the full MCU console into the UI.
            </Typography>
          </Stack>

          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            <Chip label={connection.isOpen ? 'link open' : 'link closed'} color={connection.isOpen ? 'success' : 'default'} />
            <Chip label={loadingPorts ? 'scanning ports' : `${ports.length} port${ports.length === 1 ? '' : 's'}`} />
            <Chip label={`baud ${baudRate}`} color="info" />
          </Stack>

          {portError ? (
            <Alert severity={ports.length === 0 ? 'info' : 'error'} variant="outlined">
              {portError}
            </Alert>
          ) : null}

          {ports.length > 0 ? (
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

          {ports.length === 0 ? (
            <FormHelperText sx={{ mt: -1 }}>
              {loadingPorts
                ? 'Scanning for ports...'
                : 'No ports detected. Enter the path manually if you know it.'}
            </FormHelperText>
          ) : null}

          <TextField
            label="Baud rate"
            value={baudRate}
            onChange={(event) => setBaudRate(event.target.value)}
            fullWidth
          />

          {selectedPort ? (
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
            <Button variant="contained" onClick={handleConnect} disabled={!path || busy} sx={{ flex: 1 }}>
              {busy && !connection.isOpen ? 'Connecting...' : 'Connect'}
            </Button>

            <Button variant="outlined" onClick={loadPorts} disabled={busy}>
              {loadingPorts ? 'Refreshing...' : 'Refresh'}
            </Button>

            <Button variant="outlined" color="error" onClick={handleDisconnect} disabled={busy}>
              {busy && connection.isOpen ? 'Closing...' : 'Disconnect'}
            </Button>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}