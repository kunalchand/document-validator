import React from 'react'
import {
  Container,
  Paper,
  Typography,
  Box,
  Stepper,
  Step,
  StepLabel
} from '@mui/material'
import { DocumentUploadForm } from '../components/DocumentUploadForm'
import { documentService } from '../services/documentService'

const PHASE_STEPS = [
  { label: 'Upload Rules Document', description: 'Provide the rules document' },
  { label: 'Review & Confirm', description: 'Verify extracted rules' },
  { label: 'Ready for Audit', description: 'Proceed to document audit' }
]

export const Phase1 = () => {
  const [activeStep, setActiveStep] = React.useState(0)
  const [extractedRules, setExtractedRules] = React.useState(null)

  const handleDocumentSubmit = async (payload) => {
    try {
      let response

      if (payload.type === 'file') {
        response = await documentService.extractRules(payload.content)
      } else {
        response = await documentService.extractRulesFromText(payload.content)
      }

      setExtractedRules(response.data)
      setActiveStep(1)
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to extract rules')
    }
  }

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
          Document Validator
        </Typography>
        <Typography variant="body1" color="textSecondary" gutterBottom>
          Phase 1: Rules Extraction
        </Typography>
      </Box>

      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {PHASE_STEPS.map((step) => (
          <Step key={step.label}>
            <StepLabel>
              <Typography variant="body2">{step.label}</Typography>
            </StepLabel>
          </Step>
        ))}
      </Stepper>

      <Paper elevation={2} sx={{ p: 4 }}>
        {activeStep === 0 && (
          <DocumentUploadForm
            title="Upload Rules Document"
            description="Upload or paste the document containing the rules that will be used to validate other documents. This can be a PDF, DOCX file, or raw text."
            onSubmit={handleDocumentSubmit}
            submitButtonText="Extract Rules"
            phase="phase1"
          />
        )}

        {activeStep === 1 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Extracted Rules
            </Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              {extractedRules && `${extractedRules.rules?.length || 0} rules extracted`}
            </Typography>

            <Box
              sx={{
                backgroundColor: 'grey.50',
                p: 2,
                borderRadius: 1,
                mb: 3,
                maxHeight: 400,
                overflowY: 'auto'
              }}
            >
              <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
                {JSON.stringify(extractedRules, null, 2)}
              </pre>
            </Box>

            <Typography variant="body2" color="textSecondary">
              Rules preview shown above. You can now proceed to audit documents against these rules.
            </Typography>
          </Box>
        )}
      </Paper>
    </Container>
  )
}
