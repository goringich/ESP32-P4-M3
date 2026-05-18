import { useEffect, useState } from 'react';
import {
  Alert,
  Box,
  CssBaseline,
  Stack,
  ThemeProvider,
} from '@mui/material';
import { fetchTransport } from './api/client';
import { DirectionPadPanel } from './components/DirectionPadPanel';
import { appTheme } from './theme/theme';
import type { TransportState } from './types/api';

const EMPTY_TRANSPORT: TransportState = {
  mode: 'serial',
  wifiBaseUrl: 'http://192.168.4.1',
  wifiConnected: false,
  lastError: null,
  lastTelemetryAt: null,
};

export default function PadApp() {
  const [transport, setTransport] = useState<TransportState>(EMPTY_TRANSPORT);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTransport()
      .then(setTransport)
      .catch((loadError) => {
        setError(loadError instanceof Error ? loadError.message : 'Не удалось связаться с backend');
      });
  }, []);

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
          {error ? <Alert severity="error" variant="outlined">{error}</Alert> : null}
          {transport.lastError ? (
            <Alert severity="warning" variant="outlined">
              Ошибка Wi-Fi транспорта: {transport.lastError}
            </Alert>
          ) : null}
          <DirectionPadPanel
            title="Wi-Fi пульт"
            subtitle="Прямое управление для стенда. Вертикальные кнопки держат движение, горизонтальные отправляют одиночный шаг."
            caption={`транспорт: ${transport.mode} · Wi-Fi мост: ${transport.wifiConnected ? 'активен' : 'ожидание'}`}
          />
        </Stack>
      </Box>
    </ThemeProvider>
  );
}
