import React from 'react'
import {
  Box,
  Paper,
  Typography,
  Button,
  Stack,
  Card,
  CardContent,
  Alert
} from '@mui/material'
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'
import InfoIcon from '@mui/icons-material/Info'

export const ReadyForAudit = ({ rulesCount, onProceedToAudit, onBack }) => {
  return (
    <Stack spacing={3}>
      <Alert severity="success" icon={<CheckCircleOutlineIcon />}>
        Rules have been successfully extracted and confirmed!
      </Alert>

      <Paper elevation={2} sx={{ p: 4, textAlign: 'center' }}>
        <CheckCircleOutlineIcon
          sx={{ fontSize: 80, color: 'success.main', mb: 2 }}
        />
        <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
          Ready for Document Audit
        </Typography>
        <Typography variant="body1" color="textSecondary" paragraph>
          Your rules have been extracted, reviewed, and confirmed. You can now
          proceed to audit documents against these rules.
        </Typography>
      </Paper>

      <Card>
        <CardContent>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 600 }}>
            Summary
          </Typography>
          <Stack spacing={1} sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2">Total Rules Extracted:</Typography>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>
                {rulesCount}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
              <Typography variant="body2">Status:</Typography>
              <Typography variant="body2" sx={{ fontWeight: 600, color: 'success.main' }}>
                Confirmed
              </Typography>
            </Box>
          </Stack>
        </CardContent>
      </Card>

      <Alert severity="info" icon={<InfoIcon />}>
        <Typography variant="body2" gutterBottom>
          <strong>Next Step:</strong> In Phase 2, you will upload a document to be audited.
          The system will evaluate it against the {rulesCount} rules you just confirmed.
        </Typography>
      </Alert>

      <Stack direction="row" spacing={2} sx={{ mt: 4 }}>
        <Button
          variant="outlined"
          onClick={onBack}
        >
          Back to Review
        </Button>
        <Box sx={{ ml: 'auto' }} />
        <Button
          variant="contained"
          onClick={onProceedToAudit}
          size="large"
        >
          Proceed to Phase 2: Audit Document
        </Button>
      </Stack>
    </Stack>
  )
}
