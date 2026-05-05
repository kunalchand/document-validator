import React, { useState } from 'react'
import {
  Box,
  TextField,
  Alert,
  Stack,
  Typography,
  LinearProgress
} from '@mui/material'
import { validateText } from '../utils/fileValidator'

export const TextInputArea = ({ onTextChange, loading = false, error = null }) => {
  const [text, setText] = useState('')
  const [validationErrors, setValidationErrors] = useState([])

  const handleTextChange = (e) => {
    const newText = e.target.value
    setText(newText)

    if (newText.trim().length > 0) {
      const validation = validateText(newText)
      setValidationErrors(validation.valid ? [] : validation.errors)
      if (validation.valid) {
        onTextChange(newText)
      }
    } else {
      setValidationErrors([])
      onTextChange(null)
    }
  }

  const charCount = text.length
  const maxChars = 50000

  return (
    <Box component="form" noValidate autoComplete="off">
      <Stack spacing={2}>
        <TextField
          fullWidth
          multiline
          rows={10}
          placeholder="Paste your document text here..."
          value={text}
          onChange={handleTextChange}
          disabled={loading}
          variant="outlined"
          sx={{
            '& .MuiOutlinedInput-root': {
              fontFamily: 'monospace'
            }
          }}
        />

        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}
        >
          <Typography variant="caption" color="textSecondary">
            {charCount.toLocaleString()} / {maxChars.toLocaleString()} characters
          </Typography>
          {charCount > maxChars * 0.8 && (
            <Typography variant="caption" color="warning.main">
              Approaching limit
            </Typography>
          )}
        </Box>

        {loading && (
          <Box>
            <LinearProgress />
            <Typography variant="caption" color="textSecondary" sx={{ mt: 1 }}>
              Processing your text...
            </Typography>
          </Box>
        )}

        {validationErrors.length > 0 && (
          <Stack spacing={1}>
            {validationErrors.map((error, idx) => (
              <Alert key={idx} severity="error">
                {error}
              </Alert>
            ))}
          </Stack>
        )}

        {error && (
          <Alert severity="error">
            {error}
          </Alert>
        )}
      </Stack>
    </Box>
  )
}
