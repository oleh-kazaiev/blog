import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'
import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { ColorModeContext, getAppTheme } from './theme'
import { AuthProvider } from './contexts/AuthContext'

const stored =
    typeof window !== 'undefined' ? localStorage.getItem('colorMode') : null
const prefersDark =
    typeof window !== 'undefined' &&
    window.matchMedia &&
    window.matchMedia('(prefers-color-scheme: dark)').matches
const initialMode: 'light' | 'dark' =
    stored === 'light' || stored === 'dark'
        ? stored
        : prefersDark
          ? 'dark'
          : 'light'

function Root() {
    const [mode, setMode] = React.useState<'light' | 'dark'>(initialMode)
    const colorMode = React.useMemo(
        () => ({
            mode,
            toggleColorMode: () => {
                setMode((prev) => {
                    const next = prev === 'light' ? 'dark' : 'light'
                    localStorage.setItem('colorMode', next)
                    return next
                })
            },
        }),
        [mode]
    )

    const theme = React.useMemo(() => getAppTheme(mode), [mode])

    return (
        <ColorModeContext.Provider value={colorMode}>
            <ThemeProvider theme={theme}>
                <CssBaseline />
                <AuthProvider>
                    <App />
                </AuthProvider>
            </ThemeProvider>
        </ColorModeContext.Provider>
    )
}

const root = ReactDOM.createRoot(document.getElementById('root'))
root.render(
    <React.StrictMode>
        <BrowserRouter>
            <Root />
        </BrowserRouter>
    </React.StrictMode>
)
