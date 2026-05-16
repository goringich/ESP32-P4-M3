import { alpha, createTheme } from '@mui/material/styles';

const R = 8;

export const appTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#63e6ff',
      light: '#bff6ff',
      dark: '#1c99b2',
    },
    secondary: {
      main: '#ff9b54',
      light: '#ffd4b2',
      dark: '#c56722',
    },
    success: { main: '#58d68d' },
    warning: { main: '#ffbf69' },
    error: { main: '#ff6f91' },
    info: { main: '#7aa2ff' },
    background: {
      default: '#06111a',
      paper: '#0c1723',
    },
    divider: 'rgba(255,255,255,0.08)',
    text: {
      primary: '#eef7ff',
      secondary: 'rgba(238,247,255,0.7)',
    },
  },

  shape: {
    borderRadius: R,
  },

  typography: {
    fontFamily: '"Space Grotesk", "IBM Plex Sans", "Segoe UI", sans-serif',
    h3: {
      fontWeight: 700,
      letterSpacing: '-0.03em',
    },
    h4: {
      fontWeight: 700,
      letterSpacing: '-0.025em',
    },
    h6: {
      fontWeight: 700,
      letterSpacing: '-0.01em',
    },
    overline: {
      letterSpacing: '0.18em',
      fontWeight: 700,
    },
  },

  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          overflowX: 'hidden',
          background:
            'radial-gradient(circle at top, rgba(99,230,255,0.08), transparent 28%), #06111a',
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
            'linear-gradient(180deg, rgba(12,23,35,0.9), rgba(7,15,24,0.98))',
          border: '1px solid rgba(255,255,255,0.07)',
          boxShadow:
            '0 24px 70px rgba(0,0,0,0.42), inset 0 1px 0 rgba(255,255,255,0.04)',
          backdropFilter: 'blur(14px)',
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
          fontWeight: 700,
          textTransform: 'none',
          boxShadow: 'none',
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
            background: 'rgba(255,255,255,0.03)',
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
          fontWeight: 600,
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
