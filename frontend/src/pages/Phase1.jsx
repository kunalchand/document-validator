import React, { useState } from 'react'
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
import { RulesList } from '../components/RulesList'
import { ReadyForAudit } from '../components/ReadyForAudit'
import { DUMMY_EXTRACTED_RULES } from '../constants/dummyRules'

const PHASE_STEPS = [
  { label: 'Upload Rules Document', description: 'Provide the rules document' },
  { label: 'Review & Confirm', description: 'Verify extracted rules' },
  { label: 'Ready for Audit', description: 'Proceed to document audit' }
]

export const Phase1 = () => {
  const [activeStep, setActiveStep] = useState(0)
  const [rules, setRules] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleDocumentSubmit = async (payload) => {
    setLoading(true)
    try {
      // TODO: Replace with actual API call when backend is ready
      // For now, using dummy data to demonstrate the flow
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Simulate API response with dummy data
      setRules([...DUMMY_EXTRACTED_RULES.rules])
      setActiveStep(1)
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to extract rules')
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
        {activeStep === 0 && (
          <DocumentUploadForm
            title="Upload Rules Document"
            description="Upload or paste the document containing the rules that will be used to validate other documents. This can be a PDF, DOCX file, or raw text."
            onSubmit={handleDocumentSubmit}
            submitButtonText="Extract Rules"
            phase="phase1"
          />
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
    </Container>
  )
}
