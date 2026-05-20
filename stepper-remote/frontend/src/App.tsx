import {
  alpha,
  Box,
  Chip,
  Container,
  CssBaseline,
  Grid,
  Stack,
  Tab,
  Tabs,
  ThemeProvider,
  Typography,
} from '@mui/material';
import { useState } from 'react';
import { ConsolePanel } from './components/ConsolePanel';
import { ConnectionPanel } from './components/ConnectionPanel';
import { ControlPanel } from './components/ControlPanel';
import { StatusBar } from './components/StatusBar';
import { TelemetryPanel } from './components/TelemetryPanel';
import { ToolingPanel } from './components/ToolingPanel';
import { useConsoleStream } from './hooks/useConsoleStream';
import { appTheme } from './theme/theme';

type WorkspaceView = 'overview' | 'control' | 'console';

function getInitialWorkspaceView(): WorkspaceView {
  if (typeof window === 'undefined') {
    return 'overview';
  }

  const view = new URLSearchParams(window.location.search).get('view');
  if (view === 'control' || view === 'console' || view === 'overview') {
    return view;
  }

  return 'overview';
}

function streamLabel(status: string) {
  if (status === 'live') {
    return 'живой';
  }
  if (status === 'connecting') {
    return 'подключение';
  }
  if (status === 'reconnecting') {
    return 'переподключение';
  }
  if (status === 'offline') {
    return 'офлайн';
  }
  return status;
}

export default function App() {
  const [workspaceView, setWorkspaceView] = useState<WorkspaceView>(getInitialWorkspaceView);
  const {
    logs,
    connection,
    tooling,
    telemetry,
    transport,
    streamStatus,
    streamError,
    setConnection,
    setTransport,
  } = useConsoleStream();

  return (
    <ThemeProvider theme={appTheme}>
      <CssBaseline />

      <Box
        sx={{
          minHeight: '100vh',
          position: 'relative',
          overflow: 'hidden',
          background: `
            radial-gradient(circle at 0% 0%, rgba(124,223,255,0.18), transparent 28%),
            radial-gradient(circle at 100% 0%, rgba(246,168,93,0.16), transparent 24%),
            radial-gradient(circle at 50% 100%, rgba(96,211,148,0.12), transparent 22%),
            linear-gradient(180deg, #050913 0%, #07101b 42%, #04070d 100%)
          `,
          '&::before': {
            content: '""',
            position: 'absolute',
            inset: 0,
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)
            `,
            backgroundSize: '26px 26px',
            maskImage: 'linear-gradient(180deg, rgba(0,0,0,0.5), rgba(0,0,0,1))',
            pointerEvents: 'none',
          },
        }}
      >
        <Container maxWidth="xl" sx={{ position: 'relative', py: 3.5 }}>
          <Stack spacing={2.25}>
            <Box
              sx={{
                position: 'relative',
                overflow: 'hidden',
                borderRadius: 6,
                px: { xs: 2, md: 3 },
                py: { xs: 2.25, md: 3 },
                border: '1px solid rgba(255,255,255,0.08)',
                background: `
                  linear-gradient(135deg, ${alpha('#7cdfff', 0.12)} 0%, transparent 34%),
                  linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02)),
                  rgba(7,12,22,0.86)
                `,
                boxShadow:
                  '0 24px 70px rgba(0,0,0,0.38), inset 0 1px 0 rgba(255,255,255,0.05)',
              }}
            >
              <Stack
                direction={{ xs: 'column', lg: 'row' }}
                spacing={2}
                justifyContent="space-between"
                alignItems={{ xs: 'flex-start', lg: 'center' }}
              >
                <Stack spacing={1}>
                  <Typography variant="overline" color="primary.light">
                    стенд гироплатформы
                  </Typography>

                  <Typography variant="h3">
                    ESP32-P4: управление и телеметрия
                  </Typography>

                  <Typography
                    variant="body1"
                    sx={{
                      maxWidth: 860,
                      color: 'text.secondary',
                      lineHeight: 1.7,
                    }}
                  >
                    Здесь показаны состояние платы, датчика, привода, UART и Wi-Fi.
                    Теперь Wi-Fi является основным каналом команд и телеметрии, а UART
                    остаётся параллельным мониторингом и запасным контуром.
                  </Typography>
                </Stack>

                <Stack
                  sx={{
                    px: 2,
                    py: 1.5,
                    borderRadius: 4,
                    border: '1px solid rgba(255,255,255,0.08)',
                    background: 'rgba(255,255,255,0.03)',
                    minWidth: { xs: '100%', lg: 280 },
                  }}
                  spacing={0.75}
                >
                  <Typography variant="overline" color="primary.light">
                    текущее состояние
                  </Typography>

                  <Typography variant="body2" color="text.secondary">
                    поток: {streamLabel(streamStatus)}
                  </Typography>

                  <Typography variant="body2" color="text.secondary">
                    строк в консоли: {logs.length}
                  </Typography>

                  <Typography variant="body2" color="text.secondary">
                    UART: {connection.isOpen ? 'подключен' : 'не подключен'}
                  </Typography>

                  <Typography variant="body2" color="text.secondary">
                    Wi-Fi: {transport.wifiConnected ? 'мост активен' : 'мост не поднят'}
                  </Typography>

                  <Typography
                    component="a"
                    href="/pad"
                    variant="body2"
                    sx={{ color: 'primary.light', textDecoration: 'none' }}
                  >
                    открыть простой Wi-Fi пульт
                  </Typography>
                </Stack>
              </Stack>
            </Box>

            <StatusBar
              connection={connection}
              linesCount={logs.length}
              tooling={tooling}
              transport={transport}
              streamStatus={streamStatus}
            />

            <Box
              sx={{
                borderRadius: 5,
                border: '1px solid rgba(255,255,255,0.08)',
                background: 'rgba(6,10,18,0.74)',
                backdropFilter: 'blur(22px)',
                overflow: 'hidden',
              }}
            >
              <Stack
                direction={{ xs: 'column', lg: 'row' }}
                spacing={1.5}
                justifyContent="space-between"
                alignItems={{ xs: 'flex-start', lg: 'center' }}
                sx={{
                  px: { xs: 1.5, md: 2.25 },
                  pt: 1.5,
                }}
              >
                <Tabs
                  value={workspaceView}
                  onChange={(_event, next: WorkspaceView) => setWorkspaceView(next)}
                  variant="scrollable"
                  allowScrollButtonsMobile
                >
                  <Tab value="overview" label="Обзор" />
                  <Tab value="control" label="Управление" />
                  <Tab value="console" label="Консоль" />
                </Tabs>

                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ px: { xs: 1, lg: 0 }, pb: { xs: 1, lg: 0 } }}>
                  <Chip label={`транспорт: ${transport.mode === 'wifi' ? 'wifi-first' : 'uart-only'}`} color={transport.mode === 'wifi' ? 'secondary' : 'primary'} />
                  <Chip label={transport.wifiConnected ? 'Wi-Fi приоритет активен' : 'Wi-Fi приоритет ожидает'} color={transport.wifiConnected ? 'success' : 'default'} />
                  <Chip label={connection.isOpen ? connection.path ?? 'UART подключен' : 'UART отключен'} color={connection.isOpen ? 'success' : 'default'} />
                </Stack>
              </Stack>

              <Box sx={{ p: { xs: 1.5, md: 2.25 } }}>
                {workspaceView === 'overview' ? (
                  <Grid container spacing={2}>
                    <Grid size={{ xs: 12, xl: 8 }} sx={{ minWidth: 0 }}>
                      <TelemetryPanel telemetry={telemetry} />
                    </Grid>
                    <Grid size={{ xs: 12, xl: 4 }} sx={{ minWidth: 0 }}>
                      <Stack spacing={2}>
                        <ConnectionPanel
                          connection={connection}
                          transport={transport}
                          onConnectionChange={setConnection}
                          onTransportChange={setTransport}
                        />
                        <ToolingPanel connection={connection} tooling={tooling} />
                      </Stack>
                    </Grid>
                  </Grid>
                ) : null}

                {workspaceView === 'control' ? (
                  <Grid container spacing={2}>
                    <Grid size={{ xs: 12, lg: 5, xl: 4 }} sx={{ minWidth: 0 }}>
                      <Stack spacing={2}>
                        <ConnectionPanel
                          connection={connection}
                          transport={transport}
                          onConnectionChange={setConnection}
                          onTransportChange={setTransport}
                        />
                        <Box
                          sx={{
                            p: 1.5,
                            borderRadius: 4,
                            border: '1px solid rgba(255,255,255,0.08)',
                            background: 'rgba(255,255,255,0.025)',
                          }}
                        >
                          <Stack spacing={0.6}>
                            <Typography variant="subtitle2">Порядок работы</Typography>
                            <Typography variant="body2" color="text.secondary">
                              1. Подайте питание на плату по UART или от батареи.
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              2. Переключайте транспорт на Wi-Fi только когда API реально доступен.
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              3. Для движения используйте 4-кнопочный пульт, а консоль оставляйте для диагностики.
                            </Typography>
                          </Stack>
                        </Box>
                      </Stack>
                    </Grid>
                    <Grid size={{ xs: 12, lg: 7, xl: 8 }} sx={{ minWidth: 0 }}>
                      <ControlPanel />
                    </Grid>
                  </Grid>
                ) : null}

                {workspaceView === 'console' ? (
                  <Grid container spacing={2}>
                    <Grid size={{ xs: 12, xl: 4 }} sx={{ minWidth: 0 }}>
                      <ToolingPanel connection={connection} tooling={tooling} />
                    </Grid>
                    <Grid size={{ xs: 12, xl: 8 }} sx={{ minWidth: 0 }}>
                      <ConsolePanel
                        logs={logs}
                        streamError={streamError}
                        streamMode={streamStatus === 'live' ? 'live' : 'fallback'}
                      />
                    </Grid>
                  </Grid>
                ) : null}
              </Box>
            </Box>
          </Stack>
        </Container>
      </Box>
    </ThemeProvider>
  );
}
