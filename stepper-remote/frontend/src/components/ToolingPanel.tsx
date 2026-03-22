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
      setError(buildError instanceof Error ? buildError.message : 'Unable to start build');
    }
  };

  const handleFlash = async () => {
    setError(null);

    try {
      await startFlash(portPath);
    } catch (flashError) {
      setError(flashError instanceof Error ? flashError.message : 'Unable to start flash');
    }
  };

  return (
    <Card sx={{ borderRadius: 5 }}>
      <CardContent>
        <Stack spacing={2.25}>
          <Stack spacing={0.5}>
            <Typography variant="h6">Firmware pipeline</Typography>
            <Typography variant="body2" color="text.secondary">
              Build and flash `hello_world_p4` from the same control surface. This keeps
              the serial workflow and firmware operations in one place.
            </Typography>
          </Stack>

          {tooling.isRunning ? <LinearProgress sx={{ borderRadius: 999 }} /> : null}

          {error ? <Alert severity="error" variant="outlined">{error}</Alert> : null}
          {tooling.error ? <Alert severity="warning" variant="outlined">{tooling.error}</Alert> : null}

          {connection.isOpen ? (
            <Alert severity="info" variant="outlined">
              Flash auto-closes the active serial session before running `idf.py flash`.
            </Alert>
          ) : null}

          <TextField
            label="Flash port"
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
              {tooling.currentAction === 'build' ? 'Building...' : 'Build firmware'}
            </Button>

            <Button
              variant="contained"
              color="secondary"
              onClick={handleFlash}
              disabled={tooling.isRunning || !portPath.trim()}
              sx={{ flex: 1 }}
            >
              {tooling.currentAction === 'flash' ? 'Flashing...' : 'Flash board'}
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
              <Typography variant="subtitle2">Pipeline state</Typography>
              <Typography variant="body2" color="text.secondary">
                project: {tooling.projectDir || '/home/goringich/esp/hello_world_p4'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                state: {tooling.isRunning ? `running ${tooling.currentAction}` : 'idle'}
                {tooling.lastAction ? `, last ${tooling.lastAction}` : ''}
                {tooling.lastExitCode !== null ? `, exit ${tooling.lastExitCode}` : ''}
              </Typography>
            </Stack>
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
}