import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  LinearProgress,
  Stack,
  TextField,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { startBuild, startFlash } from '../api/client';
import type { ConnectionState, ToolingState } from '../types/api';

type Props = {
  connection: ConnectionState;
  tooling: ToolingState;
};

export function ToolingPanel({ connection, tooling }: Props) {
  const [portPath, setPortPath] = useState('');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (connection.path) {
      setPortPath(connection.path);
      return;
    }

    if (!portPath && tooling.portPath) {
      setPortPath(tooling.portPath);
    }
  }, [connection.path, tooling.portPath, portPath]);

  const handleBuild = async () => {
    setError(null);

    try {
      await startBuild();
    } catch (buildError) {
      setError(buildError instanceof Error ? buildError.message : 'Не удалось запустить сборку');
    }
  };

  const handleFlash = async () => {
    setError(null);

    try {
      await startFlash(portPath);
    } catch (flashError) {
      setError(flashError instanceof Error ? flashError.message : 'Не удалось запустить прошивку');
    }
  };

  return (
    <Card sx={{ borderRadius: 5 }}>
      <CardContent>
        <Stack spacing={2.25}>
          <Stack spacing={0.5}>
            <Typography variant="h6">Сборка и прошивка</Typography>
            <Typography variant="body2" color="text.secondary">
              Здесь можно собрать текущую прошивку и прошить плату, не выходя из веб-интерфейса.
            </Typography>
          </Stack>

          {tooling.isRunning ? <LinearProgress sx={{ borderRadius: 999 }} /> : null}

          {error ? <Alert severity="error" variant="outlined">{error}</Alert> : null}
          {tooling.error ? <Alert severity="warning" variant="outlined">{tooling.error}</Alert> : null}

          {connection.isOpen ? (
            <Alert severity="info" variant="outlined">
              Перед прошивкой активная UART-сессия будет автоматически закрыта.
            </Alert>
          ) : null}

          <TextField
            label="Порт прошивки"
            value={portPath}
            onChange={(event) => setPortPath(event.target.value)}
            placeholder="/dev/ttyUSB0"
            fullWidth
          />

          <Stack direction="row" spacing={1.25}>
            <Button
              variant="contained"
              onClick={handleBuild}
              disabled={tooling.isRunning}
              sx={{ flex: 1 }}
            >
              {tooling.currentAction === 'build' ? 'Сборка...' : 'Собрать прошивку'}
            </Button>

            <Button
              variant="contained"
              color="secondary"
              onClick={handleFlash}
              disabled={tooling.isRunning || !portPath.trim()}
              sx={{ flex: 1 }}
            >
              {tooling.currentAction === 'flash' ? 'Прошивка...' : 'Прошить плату'}
            </Button>
          </Stack>

          <Box
            sx={{
              p: 1.5,
              borderRadius: 3,
              border: '1px solid rgba(255,255,255,0.06)',
              background: 'rgba(255,255,255,0.025)',
            }}
          >
            <Stack spacing={0.75}>
              <Typography variant="subtitle2">Состояние</Typography>
              <Typography variant="body2" color="text.secondary">
                проект: {tooling.projectDir || '/home/goringich/esp'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                состояние: {tooling.isRunning ? `выполняется ${tooling.currentAction}` : 'ожидание'}
                {tooling.lastAction ? `, последняя ${tooling.lastAction}` : ''}
                {tooling.lastExitCode !== null ? `, код ${tooling.lastExitCode}` : ''}
              </Typography>
            </Stack>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}
