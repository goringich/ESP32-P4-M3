import {
  Alert,
  Box,
  Button,
  Stack,
  Typography,
} from '@mui/material';
import { useState, type ReactNode } from 'react';
import { sendCommand } from '../api/client';

type DirectionButtonProps = {
  label: string;
  color: 'primary' | 'secondary' | 'inherit';
  onPress: () => Promise<void>;
  onRelease?: () => Promise<void>;
  disabled: boolean;
};

type DirectionPadPanelProps = {
  title?: string;
  subtitle?: string;
  caption?: ReactNode;
  embedded?: boolean;
};

function DirectionButton({
  label,
  color,
  onPress,
  onRelease,
  disabled,
}: DirectionButtonProps) {
  const [pressed, setPressed] = useState(false);

  const handlePress = async () => {
    if (pressed || disabled) {
      return;
    }

    setPressed(true);
    await onPress();
  };

  const handleRelease = async () => {
    if (!pressed) {
      return;
    }

    setPressed(false);

    if (onRelease) {
      await onRelease();
    }
  };

  return (
    <Button
      variant="contained"
      color={color}
      onPointerDown={() => void handlePress()}
      onPointerUp={() => void handleRelease()}
      onPointerCancel={() => void handleRelease()}
      onPointerLeave={() => void handleRelease()}
      disabled={disabled}
      sx={{
        minHeight: { xs: 88, sm: 96 },
        borderRadius: 5,
        fontSize: { xs: '1.05rem', sm: '1.2rem' },
        fontWeight: 800,
        letterSpacing: '0.08em',
        touchAction: 'none',
      }}
    >
      {label}
    </Button>
  );
}

export function DirectionPadPanel({
  title = '4-кнопочное управление',
  subtitle = 'Вверх и вниз удерживают движение, влево и вправо отправляют одиночный шаг.',
  caption,
  embedded = false,
}: DirectionPadPanelProps) {
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const run = async (command: string) => {
    setError(null);
    setBusy(true);

    try {
      await sendCommand(command);
    } catch (sendError) {
      setError(sendError instanceof Error ? sendError.message : 'Не удалось отправить команду');
    } finally {
      setBusy(false);
    }
  };

  return (
    <Stack spacing={2}>
      <Stack spacing={0.5}>
        <Typography variant={embedded ? 'subtitle1' : 'h5'} fontWeight={700}>
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {subtitle}
        </Typography>
        {caption ? (
          <Typography variant="caption" color="text.secondary">
            {caption}
          </Typography>
        ) : null}
      </Stack>

      {error ? (
        <Alert severity="error" variant="outlined">
          {error}
        </Alert>
      ) : null}

      <Box
        sx={{
          display: 'grid',
          gap: 1.25,
          gridTemplateColumns: '1fr 1fr 1fr',
          gridTemplateAreas: `
            ". up ."
            "left . right"
            ". down ."
          `,
        }}
      >
        <Box sx={{ gridArea: 'up' }}>
          <DirectionButton
            label="ВВЕРХ"
            color="primary"
            onPress={() => run('f')}
            onRelease={() => run('s')}
            disabled={busy}
          />
        </Box>
        <Box sx={{ gridArea: 'left' }}>
          <DirectionButton
            label="ВЛЕВО"
            color="secondary"
            onPress={() => run('2')}
            disabled={busy}
          />
        </Box>
        <Box sx={{ gridArea: 'right' }}>
          <DirectionButton
            label="ВПРАВО"
            color="secondary"
            onPress={() => run('1')}
            disabled={busy}
          />
        </Box>
        <Box sx={{ gridArea: 'down' }}>
          <DirectionButton
            label="ВНИЗ"
            color="primary"
            onPress={() => run('r')}
            onRelease={() => run('s')}
            disabled={busy}
          />
        </Box>
      </Box>

      <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1}>
        <Button fullWidth variant="outlined" color="error" onClick={() => void run('s')} disabled={busy}>
          Стоп
        </Button>
        <Button fullWidth variant="outlined" color="warning" onClick={() => void run('z')} disabled={busy}>
          Отпустить катушки
        </Button>
        <Button fullWidth variant="text" onClick={() => void run('p')} disabled={busy}>
          Статус
        </Button>
      </Stack>
    </Stack>
  );
}
