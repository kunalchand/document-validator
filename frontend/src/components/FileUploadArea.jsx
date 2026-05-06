import React, { useState } from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  LinearProgress,
  Stack
} from '@mui/material'
import CloudUploadIcon from '@mui/icons-material/CloudUpload'
import { validateFile } from '../utils/fileValidator'

export const FileUploadArea = ({ onFileSelect, loading = false, error = null }) => {
  const [dragActive, setDragActive] = useState(false)
  const [fileName, setFileName] = useState(null)
  const [validationErrors, setValidationErrors] = useState([])

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(e.type === 'dragenter' || e.type === 'dragover')
  }

  const handleFile = (file) => {
    const validation = validateFile(file)

    if (!validation.valid) {
      setValidationErrors(validation.errors)
      setFileName(null)
      return
    }

    setValidationErrors([])
    setFileName(file.name)
    onFileSelect(file)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  return (
    <Box>
      <Paper
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        sx={{
          p: 4,
          border: '2px dashed',
          borderColor: dragActive ? 'primary.main' : 'divider',
          backgroundColor: dragActive ? 'action.hover' : 'background.paper',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          textAlign: 'center',
          mb: 2
        }}
      >
        <Stack spacing={2} alignItems="center">
          <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main' }} />
          <Box>
            <Typography variant="h6" gutterBottom>
              Drag and drop your file here
            </Typography>
            <Typography variant="body2" color="textSecondary">
              or
            </Typography>
          </Box>
          <input
            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            style={{ display: 'none' }}
            id="file-input"
            type="file"
            onChange={handleFileInputChange}
            disabled={loading}
          />
          <label htmlFor="file-input" style={{ width: '100%' }}>
            <Button
              variant="contained"
              component="span"
              disabled={loading}
            >
              Choose File
            </Button>
          </label>
          <Typography variant="caption" color="textSecondary">
            PDF or DOCX • Max 10MB
          </Typography>
        </Stack>
      </Paper>

      {fileName && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="success.main">
            ✓ {fileName}
          </Typography>
        </Box>
      )}

      {loading && (
        <Box sx={{ mb: 2 }}>
          <LinearProgress />
          <Typography variant="caption" color="textSecondary" sx={{ mt: 1 }}>
            Processing your document...
          </Typography>
        </Box>
      )}

      {validationErrors.length > 0 && (
        <Stack spacing={1} sx={{ mb: 2 }}>
          {validationErrors.map((error, idx) => (
            <Alert key={idx} severity="error">
              {error}
            </Alert>
          ))}
        </Stack>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
    </Box>
  )
}
