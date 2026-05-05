import React, { useState } from 'react'
import {
  Box,
  Button,
  Stack,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent
} from '@mui/material'
import { DOCUMENT_TYPES } from '../constants/documentTypes'
import { DocumentTypeSelector } from './DocumentTypeSelector'
import { FileUploadArea } from './FileUploadArea'
import { TextInputArea } from './TextInputArea'

export const DocumentUploadForm = ({
  title = 'Upload Document',
  description = null,
  onSubmit,
  submitButtonText = 'Submit',
  phase = 'phase1'
}) => {
  const [documentType, setDocumentType] = useState(DOCUMENT_TYPES.FILE)
  const [selectedFile, setSelectedFile] = useState(null)
  const [textInput, setTextInput] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [successMessage, setSuccessMessage] = useState(null)

  const isValid = documentType === DOCUMENT_TYPES.FILE ? selectedFile : textInput

  const handleTypeChange = (newType) => {
    setDocumentType(newType)
    setSelectedFile(null)
    setTextInput(null)
    setError(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!isValid) {
      setError('Please provide a document before submitting')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const payload = {
        type: documentType,
        phase,
        content: documentType === DOCUMENT_TYPES.FILE ? selectedFile : textInput
      }

      await onSubmit(payload)
      setSuccessMessage('Document submitted successfully!')
      setSelectedFile(null)
      setTextInput(null)
    } catch (err) {
      setError(err.message || 'An error occurred while processing your document')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      noValidate
      autoComplete="off"
    >
      <Stack spacing={3}>
        {description && (
          <Alert severity="info">
            {description}
          </Alert>
        )}

        {successMessage && (
          <Alert severity="success" onClose={() => setSuccessMessage(null)}>
            {successMessage}
          </Alert>
        )}

        <DocumentTypeSelector
          selectedType={documentType}
          onTypeChange={handleTypeChange}
        />

        {documentType === DOCUMENT_TYPES.FILE && (
          <FileUploadArea
            onFileSelect={setSelectedFile}
            loading={loading}
            error={error}
          />
        )}

        {documentType === DOCUMENT_TYPES.TEXT && (
          <TextInputArea
            onTextChange={setTextInput}
            loading={loading}
            error={error}
          />
        )}

        <Button
          type="submit"
          variant="contained"
          size="large"
          disabled={!isValid || loading}
          fullWidth
        >
          {loading ? 'Processing...' : submitButtonText}
        </Button>
      </Stack>
    </Box>
  )
}
