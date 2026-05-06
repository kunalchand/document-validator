import React, { useState } from 'react'
import {
  Container,
  Paper,
  Typography,
  Box,
  Stepper,
  Step,
  StepLabel,
  Alert,
  Snackbar
} from '@mui/material'
import { DocumentUploadForm } from '../components/DocumentUploadForm'
import { RulesList } from '../components/RulesList'
import { ReadyForAudit } from '../components/ReadyForAudit'
import ExtractionProgress from '../components/ExtractionProgress'
import { documentService } from '../services/documentService'

const PHASE_STEPS = [
  { label: 'Upload Rules Document', description: 'Provide the rules document' },
  { label: 'Review & Confirm', description: 'Verify extracted rules' },
  { label: 'Ready for Audit', description: 'Proceed to document audit' }
]

export const Phase1 = () => {
  const [activeStep, setActiveStep] = useState(0)
  const [rules, setRules] = useState(null)
  const [loading, setLoading] = useState(false)
  const [extractionEvents, setExtractionEvents] = useState([])
  const [extractionError, setExtractionError] = useState(null)
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'warning' })

  const showNotification = (message, severity = 'warning') => {
    setNotification({ open: true, message, severity })
  }

  const handleCloseNotification = () => {
    setNotification((prev) => ({ ...prev, open: false }))
  }

  const handleDocumentSubmit = async (payload) => {
    setLoading(true)
    setExtractionEvents([])
    setExtractionError(null)

    try {
      const events = []

      await documentService.extractRulesStream(payload, (event) => {
        events.push(event)
        setExtractionEvents([...events])

        if (event.event_type === 'finalization_complete' && event.data?.extracted_rules) {
          setRules(event.data.extracted_rules)
          setActiveStep(1)
        }

        if (event.event_type === 'extraction_complete' && event.data?.failed_segments > 0) {
          const n = event.data.failed_segments
          showNotification(
            `${n} section${n > 1 ? 's' : ''} failed during extraction — results may be incomplete. Check backend logs for details.`,
            'warning'
          )
        }

        if (event.event_type === 'error') {
          setExtractionError(event.message)
          showNotification(`Extraction failed: ${event.message}`, 'error')
        }
      })
    } catch (error) {
      const msg = error.message || 'Failed to extract rules'
      setExtractionError(msg)
      showNotification(msg, 'error')
    } finally {
      setLoading(false)
    }
  }

  const handleRulesChange = (updatedRules) => {
    setRules(updatedRules)
  }

  const handleConfirmRules = () => {
    setLoading(true)
    setTimeout(() => {
      setLoading(false)
      setActiveStep(2)
    }, 500)
  }

  const handleBackToReview = () => {
    setActiveStep(1)
  }

  const handleBackToUpload = () => {
    setRules(null)
    setExtractionEvents([])
    setExtractionError(null)
    setActiveStep(0)
  }

  const handleProceedToAudit = () => {
    // TODO: Navigate to Phase 2
    console.log('Proceeding to Phase 2 with rules:', rules)
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 600 }}>
          Document Validator
        </Typography>
        <Typography variant="body1" color="textSecondary" gutterBottom>
          Phase 1: Rules Extraction & Confirmation
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
        {extractionEvents.length > 0 && activeStep < 2 && (
          <Box sx={{ mb: activeStep === 0 && !extractionError ? 0 : 3 }}>
            <ExtractionProgress events={extractionEvents} />
          </Box>
        )}

        {activeStep === 0 && (
          <Box>
            {extractionError && (
              <Alert severity="error" sx={{ mb: 3, mt: extractionEvents.length > 0 ? 3 : 0 }}>
                {extractionError}
              </Alert>
            )}

            {!loading && (
              <DocumentUploadForm
                title="Upload Rules Document"
                description="Upload or paste the document containing the rules that will be used to validate other documents. This can be a PDF, DOCX file, or raw text."
                onSubmit={handleDocumentSubmit}
                submitButtonText="Extract Rules"
                phase="phase1"
              />
            )}
          </Box>
        )}

        {activeStep === 1 && rules && (
          <Box>
            <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
              Review & Confirm Extracted Rules
            </Typography>
            <Typography variant="body2" color="textSecondary" paragraph>
              Review the extracted rules below. You can edit, add conditions, or delete rules as needed.
              Once satisfied, click "Confirm Rules & Continue" to proceed.
            </Typography>
            <RulesList
              rules={rules}
              onRulesChange={handleRulesChange}
              onConfirm={handleConfirmRules}
              onBack={handleBackToUpload}
              loading={loading}
            />
          </Box>
        )}

        {activeStep === 2 && rules && (
          <ReadyForAudit
            rulesCount={rules.length}
            onProceedToAudit={handleProceedToAudit}
            onBack={handleBackToReview}
          />
        )}
      </Paper>
      <Snackbar
        open={notification.open}
        autoHideDuration={8000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleCloseNotification}
          severity={notification.severity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Container>
  )
}
