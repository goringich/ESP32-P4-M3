import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Divider,
  Grid,
  Stack,
  Typography,
} from '@mui/material';
import { useState } from 'react';
import { pushDebugLog, sendCommand } from '../api/client';

function GroupTitle({
  title,
  subtitle,
}: {
  title: string;
  subtitle: string;
}) {
  return (
    <Stack spacing={0.25}>
      <Typography variant="subtitle1" fontWeight={700}>
        {title}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {subtitle}
      </Typography>
    </Stack>
  );
}

export function ControlPanel() {
  const [error, setError] = useState<string | null>(null);
  const [pendingCommand, setPendingCommand] = useState<string | null>(null);

  const send = async (command: string) => {
    setError(null);
    setPendingCommand(command);

    try {
      await sendCommand(command);
    } catch (sendError) {
      setError(sendError instanceof Error ? sendError.message : 'Unable to send command');
    } finally {
      setPendingCommand(null);
    }
  };

  const pushTestLog = async () => {
    setError(null);
    setPendingCommand('debug-log');

    try {
      await pushDebugLog();
    } catch (sendError) {
      setError(sendError instanceof Error ? sendError.message : 'Unable to push debug log');
    } finally {
      setPendingCommand(null);
    }
  };

  return (
    <Card sx={{ borderRadius: 5 }}>
      <CardContent>
        <Stack spacing={2.25}>
          <Stack spacing={0.5}>
            <Typography variant="h6">Drive console</Typography>
            <Typography variant="body2" color="text.secondary">
              Send direct commands into the live firmware session. Controls are grouped by motion,
              timing, phase diagnostics, and console actions.
            </Typography>
          </Stack>

          {error ? (
            <Alert severity="error" variant="outlined">
              {error}
            </Alert>
          ) : null}

          <Box
            sx={{
              p: 1.5,
              borderRadius: 3,
              background: 'linear-gradient(180deg, rgba(124,223,255,0.08), rgba(255,255,255,0.02))',
              border: '1px solid rgba(124,223,255,0.12)',
            }}
          >
            <GroupTitle
              title="Motion"
              subtitle="Primary drive states for the stepper."
            />
            <Grid container spacing={1} sx={{ mt: 1 }}>
              <Grid size={{ xs: 6, md: 6, lg: 6 }}>
                <Button fullWidth variant="contained" color="error" onClick={() => send('s')} disabled={pendingCommand !== null}>
                  Stop
                </Button>
              </Grid>
              <Grid size={{ xs: 6, md: 6, lg: 6 }}>
                <Button fullWidth variant="contained" onClick={() => send('w')} disabled={pendingCommand !== null}>
                  Sweep
                </Button>
              </Grid>
              <Grid size={{ xs: 6, md: 6, lg: 6 }}>
                <Button fullWidth variant="outlined" onClick={() => send('f')} disabled={pendingCommand !== null}>
                  Forward
                </Button>
              </Grid>
              <Grid size={{ xs: 6, md: 6, lg: 6 }}>
                <Button fullWidth variant="outlined" onClick={() => send('r')} disabled={pendingCommand !== null}>
                  Reverse
                </Button>
              </Grid>
            </Grid>
          </Box>

          <Divider />

          <Stack spacing={1.25}>
            <GroupTitle
              title="Manual stepping"
              subtitle="Short impulses for safe testing and fine positioning."
            />
            <Grid container spacing={1}>
              <Grid size={{ xs: 6, md: 6, lg: 6 }}>
                <Button fullWidth variant="outlined" onClick={() => send('1')} disabled={pendingCommand !== null}>
                  Step +
                </Button>
              </Grid>
              <Grid size={{ xs: 6, md: 6, lg: 6 }}>
                <Button fullWidth variant="outlined" onClick={() => send('2')} disabled={pendingCommand !== null}>
                  Step -
                </Button>
              </Grid>
            </Grid>
          </Stack>

          <Divider />

          <Stack spacing={1.25}>
            <GroupTitle
              title="Timing"
              subtitle="Tune motion delay directly from the panel."
            />
            <Grid container spacing={1}>
              <Grid size={{ xs: 6, md: 6, lg: 6 }}>
                <Button fullWidth variant="outlined" onClick={() => send('+')} disabled={pendingCommand !== null}>
                  Faster
                </Button>
              </Grid>
              <Grid size={{ xs: 6, md: 6, lg: 6 }}>
                <Button fullWidth variant="outlined" onClick={() => send('-')} disabled={pendingCommand !== null}>
                  Slower
                </Button>
              </Grid>
            </Grid>
          </Stack>

          <Divider />

          <Stack spacing={1.25}>
            <GroupTitle
              title="Phase diagnostics"
              subtitle="Force a specific phase and inspect driver behavior."
            />
            <Grid container spacing={1}>
              <Grid size={{ xs: 3, md: 3, lg: 3 }}>
                <Button fullWidth variant="text" onClick={() => send('a')} disabled={pendingCommand !== null}>
                  A
                </Button>
              </Grid>
              <Grid size={{ xs: 3, md: 3, lg: 3 }}>
                <Button fullWidth variant="text" onClick={() => send('b')} disabled={pendingCommand !== null}>
                  B
                </Button>
              </Grid>
              <Grid size={{ xs: 3, md: 3, lg: 3 }}>
                <Button fullWidth variant="text" onClick={() => send('c')} disabled={pendingCommand !== null}>
                  C
                </Button>
              </Grid>
              <Grid size={{ xs: 3, md: 3, lg: 3 }}>
                <Button fullWidth variant="text" onClick={() => send('d')} disabled={pendingCommand !== null}>
                  D
                </Button>
              </Grid>
            </Grid>
          </Stack>

          <Divider />

          <Stack spacing={1.25}>
            <GroupTitle
              title="Console actions"
              subtitle="MCU status request and raw log injection."
            />
            <Grid container spacing={1}>
              <Grid size={{ xs: 12, md: 12, lg: 12 }}>
                <Button fullWidth variant="outlined" color="warning" onClick={() => send('z')} disabled={pendingCommand !== null}>
                  Release coils
                </Button>
              </Grid>
              <Grid size={{ xs: 12, md: 12, lg: 12 }}>
                <Button fullWidth variant="outlined" onClick={() => send('p')} disabled={pendingCommand !== null}>
                  Request status
                </Button>
              </Grid>
              <Grid size={{ xs: 12, md: 12, lg: 12 }}>
                <Button fullWidth variant="contained" color="secondary" onClick={pushTestLog} disabled={pendingCommand !== null}>
                  {pendingCommand === 'debug-log' ? 'Pushing log...' : 'Push test console line'}
                </Button>
              </Grid>
            </Grid>
          </Stack>
        </Stack>
      </CardContent>
    </Card>
  );
}