import { alpha, createTheme } from '@mui/material/styles';

const R = 8;

export const appTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#7cdfff',
      light: '#b6f0ff',
    },
    secondary: {
      main: '#f6a85d',
      light: '#ffd3a8',
    },
    success: { main: '#60d394' },
    warning: { main: '#ffb347' },
    error: { main: '#ff6b7a' },
    background: {
      default: '#050913',
      paper: '#0b1320',
    },
    divider: 'rgba(255,255,255,0.08)',
    text: {
      primary: '#edf4ff',
      secondary: 'rgba(237,244,255,0.72)',
    },
  },

  shape: {
    borderRadius: R,
  },

  typography: {
    fontFamily: '"IBM Plex Sans", "Inter", "Segoe UI", sans-serif',
  },

  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          overflowX: 'hidden',
        },
      },
    },

    // ======================
    // CARD (главный контейнер)
    // ======================
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: R * 1.5, // 24px
          overflow: 'hidden',
          background:
            'linear-gradient(180deg, rgba(11,19,32,0.92), rgba(7,12,22,0.98))',
          border: '1px solid rgba(255,255,255,0.08)',
          boxShadow:
            '0 20px 60px rgba(0,0,0,0.38), inset 0 1px 0 rgba(255,255,255,0.03)',
        },
      },
    },

  MuiStack: {
    styleOverrides: {
      root: {
        borderRadius: 0,
        minWidth: 0,
      },
    },
  },

    MuiCardContent: {
      styleOverrides: {
        root: {
          padding: 18,
        },
      },
    },

    // ======================
    // BUTTON
    // ======================
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: R, // 16px
          minHeight: 46,
        },
      },
    },

    // ======================
    // INPUT / TEXTFIELD
    // ======================
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: R,
            background: 'rgba(255,255,255,0.02)',
          },
        },
      },
    },

    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: R,
        },
      },
    },

    // ======================
    // CHIP
    // ======================
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: R * 0.75, // 12px
        },
      },
    },

    // ======================
    // ALERT
    // ======================
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: R,
        },
      },
    },

    MuiDivider: {
      styleOverrides: {
        root: {
          borderColor: alpha('#ffffff', 0.08),
        },
      },
    },
  },
});