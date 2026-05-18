import { Box, Card, CardContent, Chip, Stack, Typography } from '@mui/material';
import type {
  ConnectionState,
  StreamStatus,
  ToolingState,
  TransportState,
} from '../types/api';

type Props = {
  connection: ConnectionState;
  linesCount: number;
  tooling: ToolingState;
  transport: TransportState;
  streamStatus: StreamStatus;
};

function streamLabel(status: StreamStatus) {
  if (status === 'live') {
    return 'живой';
  }
  if (status === 'connecting') {
    return 'подключение';
  }
  if (status === 'reconnecting') {
    return 'переподключение';
  }
  return 'офлайн';
}

export function StatusBar({ connection, linesCount, tooling, transport, streamStatus }: Props) {
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
        background:
          'linear-gradient(135deg, rgba(99,230,255,0.08), rgba(255,255,255,0.025) 36%, rgba(255,155,84,0.08) 100%)',
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
              label={
                transport.mode === 'wifi'
                  ? transport.wifiConnected
                    ? 'Wi-Fi мост подключен'
                    : 'Wi-Fi мост ожидает'
                  : connection.isOpen
                    ? 'UART подключен'
                    : 'UART отключен'
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
            <Chip label={`транспорт: ${transport.mode}`} color={transport.mode === 'wifi' ? 'secondary' : 'default'} />
            <Chip label={`порт: ${connection.path ?? '-'}`} />
            <Chip label={`baud: ${connection.baudRate ?? '-'}`} />
            <Chip label={`строк: ${linesCount}`} />
            <Chip label={`поток: ${streamLabel(streamStatus)}`} color={streamColor} />
            <Chip
              label={
                tooling.isRunning
                  ? `задача: ${tooling.currentAction}`
                  : tooling.lastAction
                    ? `последняя: ${tooling.lastAction}${tooling.lastExitCode !== null ? ` (${tooling.lastExitCode})` : ''}`
                    : 'задач нет'
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
              background: 'rgba(7, 16, 27, 0.45)',
            }}
          >
            <Typography variant="body2" color="text.secondary">
              Питание по UART и управление по Wi-Fi могут работать параллельно
            </Typography>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}
