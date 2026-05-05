import React from 'react'
import {
  Box,
  FormControl,
  FormLabel,
  RadioGroup,
  FormControlLabel,
  Radio,
  Paper
} from '@mui/material'
import { DOCUMENT_TYPES } from '../constants/documentTypes'

export const DocumentTypeSelector = ({ selectedType, onTypeChange }) => {
  return (
    <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
      <FormControl component="fieldset" fullWidth>
        <FormLabel component="legend" sx={{ mb: 2, fontWeight: 600 }}>
          How would you like to upload your document?
        </FormLabel>
        <RadioGroup
          row
          value={selectedType}
          onChange={(e) => onTypeChange(e.target.value)}
        >
          <FormControlLabel
            value={DOCUMENT_TYPES.FILE}
            control={<Radio />}
            label="Upload File (PDF/DOCX)"
          />
          <FormControlLabel
            value={DOCUMENT_TYPES.TEXT}
            control={<Radio />}
            label="Paste Text"
          />
        </RadioGroup>
      </FormControl>
    </Paper>
  )
}
