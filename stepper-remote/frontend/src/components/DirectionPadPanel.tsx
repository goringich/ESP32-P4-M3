import {
  Alert,
  Box,
  Chip,
  Stack,
  Typography,
} from '@mui/material';
import ButtonBase from '@mui/material/ButtonBase';
import { useRef, useState, type PointerEvent as ReactPointerEvent, type ReactNode } from 'react';
import { sendCommand } from '../api/client';

type DirectionButtonProps = {
  label: string;
  color: 'primary' | 'secondary';
  mode?: 'hold' | 'tap';
  onPress: () => Promise<void>;
  onRelease?: () => Promise<void>;
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
  mode = 'tap',
  onPress,
  onRelease,
}: DirectionButtonProps) {
  const [pressed, setPressed] = useState(false);
  const activePointerId = useRef<number | null>(null);

  const handlePress = async (event: ReactPointerEvent<HTMLButtonElement>) => {
    if (activePointerId.current !== null) {
      return;
    }

    activePointerId.current = event.pointerId;
    setPressed(true);
    event.currentTarget.setPointerCapture(event.pointerId);
    await onPress();
  };

  const handleRelease = async (event: ReactPointerEvent<HTMLButtonElement>) => {
    if (activePointerId.current !== event.pointerId) {
      return;
    }

    activePointerId.current = null;
    setPressed(false);

    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }

    if (mode === 'hold' && onRelease) {
      await onRelease();
    }
  };

  return (
    <ButtonBase
      onPointerDown={(event) => void handlePress(event)}
      onPointerUp={(event) => void handleRelease(event)}
      onPointerCancel={(event) => void handleRelease(event)}
      onPointerLeave={(event) => {
        if (mode === 'hold') {
          void handleRelease(event);
        }
      }}
      sx={{
        minHeight: { xs: 96, sm: 104 },
        borderRadius: 5,
        fontSize: { xs: '1.05rem', sm: '1.2rem' },
        fontWeight: 800,
        letterSpacing: '0.08em',
        color: 'common.white',
        border: '1px solid',
        borderColor:
          color === 'primary'
            ? 'rgba(124,223,255,0.45)'
            : 'rgba(246,168,93,0.45)',
        background:
          pressed
            ? color === 'primary'
              ? 'linear-gradient(180deg, rgba(124,223,255,0.34), rgba(18,65,102,0.92))'
              : 'linear-gradient(180deg, rgba(246,168,93,0.30), rgba(86,49,17,0.92))'
            : 'linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02))',
        touchAction: 'none',
      }}
    >
      {label}
    </ButtonBase>
  );
}

export function DirectionPadPanel({
  title = '4-кнопочное управление',
  subtitle = 'Все 4 стрелки работают только пока кнопка реально зажата. На отпускании всегда уходит стоп.',
  caption,
  embedded = false,
}: DirectionPadPanelProps) {
  const [error, setError] = useState<string | null>(null);
  const [driveState, setDriveState] = useState<'forward' | 'reverse' | 'left' | 'right' | 'stop'>('stop');

  const run = async (command: string) => {
    setError(null);

    try {
      await sendCommand(command);
    } catch (sendError) {
      setError(sendError instanceof Error ? sendError.message : 'Не удалось отправить команду');
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
        <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
          <Chip
            size="small"
            color={driveState === 'stop' ? 'default' : 'success'}
            label={`режим: ${
              driveState === 'forward'
                ? 'вперед'
                : driveState === 'reverse'
                  ? 'назад'
                  : driveState === 'left'
                    ? 'влево'
                    : driveState === 'right'
                      ? 'вправо'
                      : 'стоп'
            }`}
          />
          <Chip size="small" variant="outlined" label="лишние кнопки убраны" />
        </Stack>
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
            label="ВПЕРЕД"
            color="primary"
            mode="hold"
            onPress={async () => {
              setDriveState('forward');
              await run('f');
            }}
            onRelease={async () => {
              setDriveState('stop');
              await run('s');
            }}
          />
        </Box>
        <Box sx={{ gridArea: 'left' }}>
          <DirectionButton
            label="ВЛЕВО"
            color="secondary"
            mode="hold"
            onPress={async () => {
              setDriveState('left');
              await run('2');
            }}
            onRelease={async () => {
              setDriveState('stop');
              await run('s');
            }}
          />
        </Box>
        <Box sx={{ gridArea: 'right' }}>
          <DirectionButton
            label="ВПРАВО"
            color="secondary"
            mode="hold"
            onPress={async () => {
              setDriveState('right');
              await run('1');
            }}
            onRelease={async () => {
              setDriveState('stop');
              await run('s');
            }}
          />
        </Box>
        <Box sx={{ gridArea: 'down' }}>
          <DirectionButton
            label="НАЗАД"
            color="primary"
            mode="hold"
            onPress={async () => {
              setDriveState('reverse');
              await run('r');
            }}
            onRelease={async () => {
              setDriveState('stop');
              await run('s');
            }}
          />
        </Box>
      </Box>
    </Stack>
  );
}
