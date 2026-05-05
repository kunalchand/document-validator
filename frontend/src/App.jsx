import React from 'react'
import { CssBaseline, ThemeProvider, createTheme, Box } from '@mui/material'
import { Phase1 } from './pages/Phase1'

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2'
    },
    secondary: {
      main: '#dc004e'
    },
    background: {
      default: '#fafafa'
    }
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif'
  }
})

export const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
        <Phase1 />
      </Box>
    </ThemeProvider>
  )
}

export default App
