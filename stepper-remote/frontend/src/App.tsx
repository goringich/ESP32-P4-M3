import {
  alpha,
  Box,
  Container,
  CssBaseline,
  Grid,
  Stack,
  ThemeProvider,
  Typography,
} from '@mui/material';
import { ConsolePanel } from './components/ConsolePanel';
import { ConnectionPanel } from './components/ConnectionPanel';
import { ControlPanel } from './components/ControlPanel';
import { StatusBar } from './components/StatusBar';
import { TelemetryPanel } from './components/TelemetryPanel';
import { ToolingPanel } from './components/ToolingPanel';
import { useConsoleStream } from './hooks/useConsoleStream';
import { appTheme } from './theme/theme';

export default function App() {
  const {
    logs,
    connection,
    tooling,
    telemetry,
    streamStatus,
    streamError,
    setConnection,
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
                  <Typography variant="h3">
                    ESP32 control station
                  </Typography>

                  <Typography
                    variant="body1"
                    sx={{
                      maxWidth: 860,
                      color: 'text.secondary',
                      lineHeight: 1.7,
                    }}
                  >
                    Full serial console, firmware pipeline, live telemetry, and motor control
                    in one interface. This panel is designed for fast diagnostics from desktop
                    or phone, with the MCU stream always visible.
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
                    live workspace
                  </Typography>

                  <Typography variant="body2" color="text.secondary">
                    stream: {streamStatus}
                  </Typography>

                  <Typography variant="body2" color="text.secondary">
                    console lines: {logs.length}
                  </Typography>

                  <Typography variant="body2" color="text.secondary">
                    serial: {connection.isOpen ? 'connected' : 'disconnected'}
                  </Typography>
                </Stack>
              </Stack>
            </Box>

            <StatusBar
              connection={connection}
              linesCount={logs.length}
              tooling={tooling}
              streamStatus={streamStatus}
            />

            <Grid container spacing={2}>
              <Grid size={{ xs: 12, xl: 4 }} sx={{ minWidth: 0 }}>
                <Stack spacing={2}>
                  <ConnectionPanel
                    connection={connection}
                    onConnectionChange={setConnection}
                  />
                  <ToolingPanel connection={connection} tooling={tooling} />
                  <ControlPanel />
                </Stack>
              </Grid>

              <Grid size={{ xs: 12, xl: 8 }} sx={{ minWidth: 0 }}>
                <Stack spacing={2}>
                  <TelemetryPanel telemetry={telemetry} />
                  <ConsolePanel
                    logs={logs}
                    streamError={streamError}
                    streamMode={streamStatus === 'live' ? 'live' : 'fallback'}
                  />
                </Stack>
              </Grid>
            </Grid>
          </Stack>
        </Container>
      </Box>
    </ThemeProvider>
  );
}