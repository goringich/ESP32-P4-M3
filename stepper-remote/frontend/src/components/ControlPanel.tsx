import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Divider,
  Grid,
  Stack,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from '@mui/material';
import { useState } from 'react';
import { pushDebugLog, sendCommand } from '../api/client';
import { DirectionPadPanel } from './DirectionPadPanel';

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
  const [view, setView] = useState<'pad' | 'console'>('pad');

  const send = async (command: string) => {
    setError(null);
    setPendingCommand(command);

    try {
      await sendCommand(command);
    } catch (sendError) {
      setError(sendError instanceof Error ? sendError.message : 'Не удалось отправить команду');
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
      setError(sendError instanceof Error ? sendError.message : 'Не удалось добавить тестовую строку в лог');
    } finally {
      setPendingCommand(null);
    }
  };

  return (
    <Card sx={{ borderRadius: 5 }}>
      <CardContent>
        <Stack spacing={2.25}>
          <Stack spacing={0.5}>
            <Typography variant="h6">Управление приводом</Typography>
            <Typography variant="body2" color="text.secondary">
              Здесь можно выбрать простой пульт или полный инженерный режим.
              Пульт нужен для обычного движения, а полный режим открывает все команды прошивки.
            </Typography>
          </Stack>

          <ToggleButtonGroup
            exclusive
            color="primary"
            value={view}
            onChange={(_event, next: 'pad' | 'console' | null) => {
              if (next) {
                setView(next);
              }
            }}
            size="small"
          >
            <ToggleButton value="pad">4 кнопки</ToggleButton>
            <ToggleButton value="console">Полный режим</ToggleButton>
          </ToggleButtonGroup>

          {error ? (
            <Alert severity="error" variant="outlined">
              {error}
            </Alert>
          ) : null}

          {view === 'pad' ? (
            <DirectionPadPanel
              embedded
              subtitle="Быстрое управление без лишних кнопок. Подходит для движения вперёд, назад и одиночных шагов."
            />
          ) : null}

          {view === 'console' ? (
            <>

              <Box
                sx={{
                  p: 1.5,
                  borderRadius: 3,
                  background: 'linear-gradient(180deg, rgba(124,223,255,0.08), rgba(255,255,255,0.02))',
                  border: '1px solid rgba(124,223,255,0.12)',
                }}
              >
                <GroupTitle
                  title="Движение"
                  subtitle="Основные режимы работы шагового привода."
                />
                <Grid container spacing={1} sx={{ mt: 1 }}>
                  <Grid size={{ xs: 6, md: 6, lg: 6 }}>
                    <Button fullWidth variant="contained" color="error" onClick={() => send('s')} disabled={pendingCommand !== null}>
                      Стоп
                    </Button>
                  </Grid>
                  <Grid size={{ xs: 6, md: 6, lg: 6 }}>
                    <Button fullWidth variant="contained" onClick={() => send('w')} disabled={pendingCommand !== null}>
                      Качание
                    </Button>
                  </Grid>
                  <Grid size={{ xs: 6, md: 6, lg: 6 }}>
                    <Button fullWidth variant="outlined" onClick={() => send('f')} disabled={pendingCommand !== null}>
                      Вперёд
                    </Button>
                  </Grid>
                  <Grid size={{ xs: 6, md: 6, lg: 6 }}>
                    <Button fullWidth variant="outlined" onClick={() => send('r')} disabled={pendingCommand !== null}>
                      Назад
                    </Button>
                  </Grid>
                </Grid>
              </Box>

              <Divider />

              <Stack spacing={1.25}>
                <GroupTitle
                  title="Одиночные шаги"
                  subtitle="Короткие импульсы для точной подстройки."
                />
                <Grid container spacing={1}>
                  <Grid size={{ xs: 6, md: 6, lg: 6 }}>
                    <Button fullWidth variant="outlined" onClick={() => send('1')} disabled={pendingCommand !== null}>
                      Шаг +
                    </Button>
                  </Grid>
                  <Grid size={{ xs: 6, md: 6, lg: 6 }}>
                    <Button fullWidth variant="outlined" onClick={() => send('2')} disabled={pendingCommand !== null}>
                      Шаг -
                    </Button>
                  </Grid>
                </Grid>
              </Stack>

              <Divider />

              <Stack spacing={1.25}>
                <GroupTitle
                  title="Скорость"
                  subtitle="Изменение задержки шага прямо из веб-интерфейса."
                />
                <Grid container spacing={1}>
                  <Grid size={{ xs: 6, md: 6, lg: 6 }}>
                    <Button fullWidth variant="outlined" onClick={() => send('+')} disabled={pendingCommand !== null}>
                      Быстрее
                    </Button>
                  </Grid>
                  <Grid size={{ xs: 6, md: 6, lg: 6 }}>
                    <Button fullWidth variant="outlined" onClick={() => send('-')} disabled={pendingCommand !== null}>
                      Медленнее
                    </Button>
                  </Grid>
                </Grid>
              </Stack>

              <Divider />

              <Stack spacing={1.25}>
                <GroupTitle
                  title="Фазы драйвера"
                  subtitle="Принудительное включение фаз для диагностики."
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
                  title="Служебные команды"
                  subtitle="Запрос статуса и тестовые записи в лог."
                />
                <Grid container spacing={1}>
                  <Grid size={{ xs: 12, md: 12, lg: 12 }}>
                    <Button fullWidth variant="outlined" color="warning" onClick={() => send('z')} disabled={pendingCommand !== null}>
                      Отпустить катушки
                    </Button>
                  </Grid>
                  <Grid size={{ xs: 12, md: 12, lg: 12 }}>
                    <Button fullWidth variant="outlined" onClick={() => send('p')} disabled={pendingCommand !== null}>
                      Запросить статус
                    </Button>
                  </Grid>
                  <Grid size={{ xs: 12, md: 12, lg: 12 }}>
                    <Button fullWidth variant="contained" color="secondary" onClick={pushTestLog} disabled={pendingCommand !== null}>
                      {pendingCommand === 'debug-log' ? 'Отправка...' : 'Добавить тестовую строку в лог'}
                    </Button>
                  </Grid>
                </Grid>
              </Stack>
            </>
          ) : null}
        </Stack>
      </CardContent>
    </Card>
  );
}
