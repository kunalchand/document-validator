import React from 'react'
import { CssBaseline, ThemeProvider, createTheme, Box } from '@mui/material'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Phase1 } from './pages/Phase1'
import ExtractionProgressDemo from './pages/ExtractionProgressDemo'

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
    <Router>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
          <Routes>
            <Route path="/" element={<Phase1 />} />
            <Route path="/demo/extraction-progress" element={<ExtractionProgressDemo />} />
          </Routes>
        </Box>
      </ThemeProvider>
    </Router>
  )
}

export default App
