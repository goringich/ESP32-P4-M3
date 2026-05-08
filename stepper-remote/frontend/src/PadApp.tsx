import { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  Button,
  CssBaseline,
  Stack,
  ThemeProvider,
  Typography,
} from '@mui/material';
import { fetchTransport, sendCommand } from './api/client';
import { appTheme } from './theme/theme';
import type { TransportState } from './types/api';

const EMPTY_TRANSPORT: TransportState = {
  mode: 'serial',
  wifiBaseUrl: 'http://192.168.4.1',
  wifiConnected: false,
  lastError: null,
  lastTelemetryAt: null,
};

type DirectionButtonProps = {
  label: string;
  color: 'primary' | 'secondary' | 'inherit';
  onPress: () => Promise<void>;
  onRelease?: () => Promise<void>;
};

function DirectionButton({ label, color, onPress, onRelease }: DirectionButtonProps) {
  const [busy, setBusy] = useState(false);

  const handlePress = async () => {
    setBusy(true);
    try {
      await onPress();
    } finally {
      setBusy(false);
    }
  };

  const handleRelease = async () => {
    if (!onRelease) {
      return;
    }
    await onRelease();
  };

  return (
    <Button
      variant="contained"
      color={color}
      onMouseDown={() => void handlePress()}
      onMouseUp={() => void handleRelease()}
      onMouseLeave={() => void handleRelease()}
      onTouchStart={() => void handlePress()}
      onTouchEnd={() => void handleRelease()}
      disabled={busy}
      sx={{
        minHeight: 96,
        borderRadius: 5,
        fontSize: '1.35rem',
        fontWeight: 800,
        letterSpacing: '0.08em',
      }}
    >
      {label}
    </Button>
  );
}

export default function PadApp() {
  const [transport, setTransport] = useState<TransportState>(EMPTY_TRANSPORT);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTransport()
      .then(setTransport)
      .catch((loadError) => {
        setError(loadError instanceof Error ? loadError.message : 'Unable to reach backend');
      });
  }, []);

  const run = async (command: string) => {
    setError(null);
    try {
      await sendCommand(command);
    } catch (sendError) {
      setError(sendError instanceof Error ? sendError.message : 'Unable to send command');
    }
  };

  return (
    <ThemeProvider theme={appTheme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: '100vh',
          display: 'grid',
          placeItems: 'center',
          px: 2,
          background:
            'radial-gradient(circle at top, rgba(124,223,255,0.18), transparent 26%), linear-gradient(180deg, #050913 0%, #04070d 100%)',
        }}
      >
        <Stack spacing={2.5} sx={{ width: '100%', maxWidth: 420 }}>
          <Stack spacing={0.75} alignItems="center">
            <Typography variant="h4">Wi-Fi motor pad</Typography>
            <Typography variant="body2" color="text.secondary" textAlign="center">
              Up/down hold the motor in motion. Left/right send one discrete step.
            </Typography>
            <Typography variant="caption" color="text.secondary">
              transport: {transport.mode} · wifi bridge: {transport.wifiConnected ? 'live' : 'waiting'}
            </Typography>
          </Stack>

          {error ? <Alert severity="error" variant="outlined">{error}</Alert> : null}
          {transport.lastError ? (
            <Alert severity="warning" variant="outlined">
              backend transport warning: {transport.lastError}
            </Alert>
          ) : null}

          <Box
            sx={{
              display: 'grid',
              gap: 1.25,
              gridTemplateColumns: '1fr 1fr 1fr',
              gridTemplateAreas: `
                ". up ."
                "left . right"
                ". down ."
              `,
            }}
          >
            <Box sx={{ gridArea: 'up' }}>
              <DirectionButton
                label="UP"
                color="primary"
                onPress={() => run('f')}
                onRelease={() => run('s')}
              />
            </Box>
            <Box sx={{ gridArea: 'left' }}>
              <DirectionButton label="LEFT" color="secondary" onPress={() => run('2')} />
            </Box>
            <Box sx={{ gridArea: 'right' }}>
              <DirectionButton label="RIGHT" color="secondary" onPress={() => run('1')} />
            </Box>
            <Box sx={{ gridArea: 'down' }}>
              <DirectionButton
                label="DOWN"
                color="primary"
                onPress={() => run('r')}
                onRelease={() => run('s')}
              />
            </Box>
          </Box>
        </Stack>
      </Box>
    </ThemeProvider>
  );
}
