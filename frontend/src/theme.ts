import React from 'react'
import { createTheme } from '@mui/material/styles'

export const ColorModeContext = React.createContext({
    mode: 'light',
    toggleColorMode: () => {},
})

export const getAppTheme = (mode: 'light' | 'dark' = 'light') =>
    createTheme({
        palette: {
            mode,
            primary: { main: mode === 'dark' ? '#90caf9' : '#1e88e5' },
            secondary: { main: mode === 'dark' ? '#ce93d8' : '#8e24aa' },
            background: { default: mode === 'dark' ? '#121212' : '#fafafa' },
            // App chrome (navbar/footer) colors: dark uses near-black; light uses a subtle neutral (not blue)
            appChrome: mode === 'dark' ? '#121212' : '#f0f2f5',
        } as any,
        shape: { borderRadius: 10 },
        components: {
            MuiAppBar: { defaultProps: { elevation: 1 } },
            MuiCard: { styleOverrides: { root: { borderRadius: 12 } } },
            MuiButton: { defaultProps: { variant: 'contained' } },
        },
        typography: {
            fontFamily: 'Inter, Roboto, Helvetica, Arial, sans-serif',
            h1: { fontSize: '2.2rem', fontWeight: 700 },
            h2: { fontSize: '1.8rem', fontWeight: 700 },
            h3: { fontSize: '1.5rem', fontWeight: 600 },
        },
    })
