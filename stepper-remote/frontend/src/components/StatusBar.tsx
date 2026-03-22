import { Box, Card, CardContent, Chip, Stack, Typography } from '@mui/material';
import type { ConnectionState, StreamStatus, ToolingState } from '../types/api';

type Props = {
  connection: ConnectionState;
  linesCount: number;
  tooling: ToolingState;
  streamStatus: StreamStatus;
};

export function StatusBar({ connection, linesCount, tooling, streamStatus }: Props) {
  const streamColor =
    streamStatus === 'live'
      ? 'success'
      : streamStatus === 'reconnecting'
        ? 'warning'
        : streamStatus === 'connecting'
          ? 'info'
          : 'default';

  return (
    <Card
      sx={{
        borderRadius: 5,
        background: 'rgba(8, 14, 24, 0.88)',
      }}
    >
      <CardContent sx={{ py: '14px !important', px: { xs: 1.5, md: 2 } }}>
        <Stack
          direction={{ xs: 'column', lg: 'row' }}
          spacing={1.25}
          justifyContent="space-between"
          alignItems={{ xs: 'flex-start', lg: 'center' }}
        >
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
            <Chip
              label={connection.isOpen ? 'serial connected' : 'serial disconnected'}
              color={connection.isOpen ? 'success' : 'default'}
            />
            <Chip label={`port: ${connection.path ?? '-'}`} />
            <Chip label={`baud: ${connection.baudRate ?? '-'}`} />
            <Chip label={`lines: ${linesCount}`} />
            <Chip label={`stream: ${streamStatus}`} color={streamColor} />
            <Chip
              label={
                tooling.isRunning
                  ? `tooling: ${tooling.currentAction}`
                  : tooling.lastAction
                    ? `last: ${tooling.lastAction}${tooling.lastExitCode !== null ? ` (${tooling.lastExitCode})` : ''}`
                    : 'tooling idle'
              }
              color={tooling.isRunning ? 'warning' : tooling.lastExitCode === 0 ? 'success' : 'default'}
            />
          </Stack>

          <Box
            sx={{
              px: 1.5,
              py: 0.75,
              borderRadius: 3,
              border: '1px solid rgba(255,255,255,0.06)',
              background: 'rgba(255,255,255,0.025)',
            }}
          >
            <Typography variant="body2" color="text.secondary">
              live serial workspace mirrored to the UI
            </Typography>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}