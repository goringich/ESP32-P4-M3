import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  Stack,
  Switch,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useMemo, useRef, useState } from 'react';
import type { LogEntry } from '../types/api';

type Props = {
  logs: LogEntry[];
  streamError: string | null;
  streamMode?: 'live' | 'fallback';
};

export function ConsolePanel({ logs, streamError, streamMode = 'live' }: Props) {
  const [filter, setFilter] = useState('');
  const [autoScroll, setAutoScroll] = useState(true);
  const tailRef = useRef<HTMLDivElement | null>(null);

  const visibleLogs = useMemo(() => {
    const query = filter.trim().toLowerCase();
    const baseLogs = logs.filter((item) => !item.line.startsWith('@telemetry '));

    if (!query) {
      return baseLogs;
    }

    return baseLogs.filter((item) => item.line.toLowerCase().includes(query));
  }, [filter, logs]);

  useEffect(() => {
    if (!autoScroll) {
      return;
    }

    tailRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [visibleLogs.length, autoScroll]);

  const counters = useMemo(() => {
    let errors = 0;
    let warnings = 0;

    for (const entry of visibleLogs) {
      if (entry.line.includes('E (') || entry.line.includes(' error')) {
        errors++;
      }
      if (entry.line.includes('W (') || entry.line.includes(' warning')) {
        warnings++;
      }
    }

    return {
      errors,
      warnings,
    };
  }, [visibleLogs]);

  return (
    <Card>
      <CardContent>
        <Stack spacing={2}>
          <Stack
            direction={{ xs: 'column', md: 'row' }}
            spacing={1.25}
            justifyContent="space-between"
            alignItems={{ xs: 'flex-start', md: 'center' }}
          >
            <Stack spacing={0.5}>
              <Typography variant="h6">Raw MCU console</Typography>
              <Typography variant="body2" color="text.secondary">
                Full serial stream from the board, including firmware logs, MPU output,
                Wi-Fi messages, and manual actions.
              </Typography>
            </Stack>

            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              <Chip label={`${visibleLogs.length} lines`} />
              <Chip label={`${counters.warnings} warnings`} color={counters.warnings > 0 ? 'warning' : 'default'} />
              <Chip label={`${counters.errors} errors`} color={counters.errors > 0 ? 'error' : 'default'} />
              <Chip label={streamMode === 'live' ? 'live stream' : 'polling fallback'} color={streamMode === 'live' ? 'success' : 'info'} />
            </Stack>
          </Stack>

          {streamError ? (
            <Alert severity="warning" variant="outlined">
              {streamError}
            </Alert>
          ) : null}

          {streamMode === 'fallback' ? (
            <Alert severity="info" variant="outlined">
              Live stream is unstable, console is using snapshot polling fallback.
            </Alert>
          ) : null}

          <Stack direction={{ xs: 'column', md: 'row' }} spacing={1.5}>
            <TextField
              label="Filter"
              value={filter}
              onChange={(event) => setFilter(event.target.value)}
              fullWidth
              placeholder="stepper, MPU, wifi, error..."
            />

            <Stack
              direction="row"
              spacing={1}
              alignItems="center"
              sx={{
                px: 1.5,
                borderRadius: 3,
                border: '1px solid rgba(255,255,255,0.08)',
                background: 'rgba(255,255,255,0.025)',
                minWidth: 170,
              }}
            >
              <Switch checked={autoScroll} onChange={(event) => setAutoScroll(event.target.checked)} />
              <Typography variant="body2" color="text.secondary">
                auto scroll
              </Typography>
            </Stack>
          </Stack>

          <Box
            sx={{
              position: 'relative',
              overflow: 'hidden',
              borderRadius: 4,
              border: '1px solid rgba(255,255,255,0.08)',
              background: `
                linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)),
                #090d14
              `,
            }}
          >
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 0.8,
                px: 1.5,
                py: 1,
                borderBottom: '1px solid rgba(255,255,255,0.06)',
                background: 'rgba(255,255,255,0.02)',
              }}
            >
              <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: '#ff5f56' }} />
              <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: '#ffbd2e' }} />
              <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: '#27c93f' }} />
              <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                serial-monitor://esp32/live-console
              </Typography>
            </Box>

            <Box
              sx={{
                color: '#d7dde8',
                p: 2,
                height: 560,
                overflow: 'auto',
                overflowX: 'hidden',
                minWidth: 0,
                fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
                fontSize: 13,
                display: 'flex',
                flexDirection: 'column',
                gap: 1,
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
              }}
            >
              {visibleLogs.length === 0 ? (
                <Box
                  sx={{
                    display: 'grid',
                    placeItems: 'center',
                    flex: 1,
                    textAlign: 'center',
                    color: 'rgba(215, 221, 232, 0.7)',
                    gap: 1,
                  }}
                >
                  <Typography variant="subtitle2" sx={{ color: 'inherit' }}>
                    {filter.trim()
                      ? 'No console lines match the current filter.'
                      : 'Waiting for serial output.'}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'inherit', maxWidth: 460 }}>
                    {filter.trim()
                      ? 'Clear the filter or search with a broader keyword.'
                      : 'Connect the board and the full MCU stream will appear here.'}
                  </Typography>
                </Box>
              ) : (
                visibleLogs.map((entry) => {
                  const isError = entry.line.includes('E (') || entry.line.includes(' error');
                  const isWarn = entry.line.includes('W (') || entry.line.includes(' warning');
                  const isTx = entry.line.startsWith('[tx]');
                  const time = new Date(entry.ts).toLocaleTimeString();

                  return (
                    <Box
                      key={entry.id}
                      sx={{
                        display: 'grid',
                        gridTemplateColumns: '88px 1fr',
                        gap: 1.5,
                        alignItems: 'start',
                        px: 1.25,
                        py: 0.9,
                        borderRadius: 2.5,
                        background: isError
                          ? 'rgba(255,107,122,0.08)'
                          : isWarn
                            ? 'rgba(255,179,71,0.08)'
                            : isTx
                              ? 'rgba(124,223,255,0.08)'
                              : 'rgba(255,255,255,0.015)',
                        border: '1px solid rgba(255,255,255,0.04)',
                      }}
                    >
                      <Typography
                        variant="caption"
                        sx={{
                          color: 'rgba(215, 221, 232, 0.55)',
                          fontFamily: 'inherit',
                          pt: '2px',
                        }}
                      >
                        {time}
                      </Typography>

                      <Box
                        component="pre"
                        sx={{
                          m: 0,
                          minWidth: 0,
                          overflowWrap: 'anywhere',
                          color: isError
                            ? '#ffd7dc'
                            : isWarn
                              ? '#ffe4bf'
                              : isTx
                                ? '#d9f8ff'
                                : '#f3f7ff',
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word',
                        }}
                      >
                        {entry.line}
                      </Box>
                    </Box>
                  );
                })
              )}

              <Box ref={tailRef} />
            </Box>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}