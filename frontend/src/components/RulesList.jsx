import React, { useState } from 'react'
import {
  Box,
  Typography,
  Button,
  Stack,
  Alert,
  Paper,
  Chip,
  TextField,
  InputAdornment
} from '@mui/material'
import SearchIcon from '@mui/icons-material/Search'
import { RuleCard } from './RuleCard'
import { ConfirmationDialog } from './ConfirmationDialog'

export const RulesList = ({ rules, onRulesChange, onConfirm, onBack, loading = false }) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterSeverity, setFilterSeverity] = useState(null)
  const [showBackConfirmation, setShowBackConfirmation] = useState(false)

  const filteredRules = rules.filter((rule) => {
    const matchesSearch =
      rule.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rule.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesSeverity = !filterSeverity || rule.severity === filterSeverity

    return matchesSearch && matchesSeverity
  })

  const handleUpdateRule = (updatedRule) => {
    const updatedRules = rules.map((rule) =>
      rule.id === updatedRule.id ? updatedRule : rule
    )
    onRulesChange(updatedRules)
  }

  const handleDeleteRule = (ruleId) => {
    const updatedRules = rules.filter((rule) => rule.id !== ruleId)
    onRulesChange(updatedRules)
  }

  const severityCounts = {
    high: rules.filter((r) => r.severity === 'high').length,
    medium: rules.filter((r) => r.severity === 'medium').length,
    low: rules.filter((r) => r.severity === 'low').length
  }

  return (
    <Stack spacing={3}>
      <Paper elevation={1} sx={{ p: 2 }}>
        <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
          Rule Summary
        </Typography>
        <Stack direction="row" spacing={2} sx={{ mt: 1 }}>
          <Box>
            <Typography variant="h6">{rules.length}</Typography>
            <Typography variant="caption" color="textSecondary">
              Total Rules
            </Typography>
          </Box>
          <Box>
            <Typography variant="h6" color="error.main">
              {severityCounts.high}
            </Typography>
            <Typography variant="caption" color="textSecondary">
              High Severity
            </Typography>
          </Box>
          <Box>
            <Typography variant="h6" color="warning.main">
              {severityCounts.medium}
            </Typography>
            <Typography variant="caption" color="textSecondary">
              Medium Severity
            </Typography>
          </Box>
          <Box>
            <Typography variant="h6" color="success.main">
              {severityCounts.low}
            </Typography>
            <Typography variant="caption" color="textSecondary">
              Low Severity
            </Typography>
          </Box>
        </Stack>
      </Paper>

      <Box>
        <TextField
          fullWidth
          placeholder="Search rules by title or description..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          variant="outlined"
          size="small"
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            )
          }}
          sx={{ mb: 2 }}
        />

        <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap' }}>
          {['high', 'medium', 'low'].map((severity) => (
            <Chip
              key={severity}
              label={severity.charAt(0).toUpperCase() + severity.slice(1)}
              onClick={() =>
                setFilterSeverity(filterSeverity === severity ? null : severity)
              }
              variant={filterSeverity === severity ? 'filled' : 'outlined'}
              color={
                severity === 'high'
                  ? 'error'
                  : severity === 'medium'
                  ? 'warning'
                  : 'success'
              }
            />
          ))}
        </Stack>
      </Box>

      {filteredRules.length === 0 ? (
        <Alert severity="info">
          {searchTerm || filterSeverity
            ? 'No rules match your search or filter criteria.'
            : 'No rules to display.'}
        </Alert>
      ) : (
        <Box>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
            Showing {filteredRules.length} of {rules.length} rules
          </Typography>
          {filteredRules.map((rule) => (
            <RuleCard
              key={rule.id}
              rule={rule}
              onUpdate={handleUpdateRule}
              onDelete={handleDeleteRule}
            />
          ))}
        </Box>
      )}

      <Stack
        direction="row"
        spacing={2}
        sx={{
          mt: 4,
          pt: 3,
          borderTop: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Button
          variant="outlined"
          onClick={() => setShowBackConfirmation(true)}
          disabled={loading}
        >
          Upload New Document
        </Button>
        <Box sx={{ ml: 'auto' }} />
        <Button
          variant="contained"
          onClick={onConfirm}
          disabled={loading || rules.length === 0}
          size="large"
        >
          {loading ? 'Confirming...' : 'Confirm Rules & Continue'}
        </Button>
      </Stack>

      <ConfirmationDialog
        open={showBackConfirmation}
        title="Change Rules Document?"
        message="Are you sure you want to go back? All extracted rules will be discarded, and you will need to upload a new document. Any edits you made will be lost."
        confirmText="Yes, Change Document"
        cancelText="Keep Reviewing"
        onConfirm={() => {
          setShowBackConfirmation(false)
          onBack()
        }}
        onCancel={() => setShowBackConfirmation(false)}
        severity="warning"
        confirmColor="warning"
      />
    </Stack>
  )
}
