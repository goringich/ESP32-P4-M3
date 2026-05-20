import {
  Alert,
  Card,
  CardContent,
  Stack,
  Typography,
} from '@mui/material';
import { useState } from 'react';
import { DirectionPadPanel } from './DirectionPadPanel';

export function ControlPanel() {
  const [error, setError] = useState<string | null>(null);

  return (
    <Card sx={{ borderRadius: 5 }}>
      <CardContent>
        <Stack spacing={2.25}>
          <Stack spacing={0.5}>
            <Typography variant="h6">Управление приводом</Typography>
            <Typography variant="body2" color="text.secondary">
              Оставлен только безопасный режим на 4 стрелки. Любая стрелка держит
              движение только пока палец реально на кнопке, на отпускании всегда
              отправляется стоп.
            </Typography>
          </Stack>

          {error ? (
            <Alert severity="error" variant="outlined">
              {error}
            </Alert>
          ) : null}

          <DirectionPadPanel
            embedded
            subtitle="Только 4 стрелки: вперед, назад, влево и вправо работают только по удержанию."
          />
        </Stack>
      </CardContent>
    </Card>
  );
}
