import React, { useState } from 'react'
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Box,
  Chip,
  Collapse,
  TextField,
  IconButton,
  Stack,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material'
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import SaveIcon from '@mui/icons-material/Save'
import CancelIcon from '@mui/icons-material/Cancel'

const SEVERITY_COLORS = {
  high: 'error',
  medium: 'warning',
  low: 'success'
}

export const RuleCard = ({ rule, onUpdate, onDelete }) => {
  const [expanded, setExpanded] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [deleteDialog, setDeleteDialog] = useState(false)
  const [editedRule, setEditedRule] = useState(rule)

  const handleEdit = () => {
    setIsEditing(true)
    setEditedRule({ ...rule })
  }

  const handleSave = () => {
    onUpdate(editedRule)
    setIsEditing(false)
  }

  const handleCancel = () => {
    setEditedRule(rule)
    setIsEditing(false)
  }

  const handleFieldChange = (field, value) => {
    setEditedRule((prev) => ({
      ...prev,
      [field]: value
    }))
  }

  const handleArrayFieldChange = (field, index, value) => {
    const updatedArray = [...editedRule[field]]
    updatedArray[index] = value
    setEditedRule((prev) => ({
      ...prev,
      [field]: updatedArray
    }))
  }

  const handleAddArrayItem = (field) => {
    setEditedRule((prev) => ({
      ...prev,
      [field]: [...prev[field], '']
    }))
  }

  const handleRemoveArrayItem = (field, index) => {
    const updatedArray = editedRule[field].filter((_, i) => i !== index)
    setEditedRule((prev) => ({
      ...prev,
      [field]: updatedArray
    }))
  }

  const handleDeleteConfirm = () => {
    onDelete(rule.id)
    setDeleteDialog(false)
  }

  const displayedRule = isEditing ? editedRule : rule

  return (
    <>
      <Card sx={{ mb: 2, border: '1px solid', borderColor: 'divider' }}>
        <CardContent>
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'flex-start',
              mb: 2
            }}
          >
            <Box flex={1}>
              {isEditing ? (
                <TextField
                  fullWidth
                  label="Rule Title"
                  value={displayedRule.title}
                  onChange={(e) => handleFieldChange('title', e.target.value)}
                  variant="outlined"
                  size="small"
                  sx={{ mb: 1 }}
                />
              ) : (
                <Typography variant="h6" component="h3" gutterBottom>
                  {displayedRule.title}
                </Typography>
              )}
            </Box>
            <Box sx={{ display: 'flex', gap: 1, ml: 2 }}>
              <Chip
                label={displayedRule.severity}
                color={SEVERITY_COLORS[displayedRule.severity]}
                size="small"
                variant="outlined"
              />
              <Chip
                label={displayedRule.status}
                variant="outlined"
                size="small"
              />
            </Box>
          </Box>

          {isEditing ? (
            <TextField
              fullWidth
              label="Description"
              value={displayedRule.description}
              onChange={(e) => handleFieldChange('description', e.target.value)}
              variant="outlined"
              size="small"
              multiline
              rows={2}
              sx={{ mb: 2 }}
            />
          ) : (
            <Typography variant="body2" color="textSecondary" paragraph>
              {displayedRule.description}
            </Typography>
          )}

          <Box sx={{ mb: 1 }}>
            <Typography variant="caption" color="textSecondary" display="block">
              Section: {displayedRule.section}
            </Typography>
          </Box>
        </CardContent>

        {!isEditing && (
          <CardActions sx={{ pb: 1 }}>
            <IconButton
              size="small"
              onClick={() => setExpanded(!expanded)}
              aria-expanded={expanded}
            >
              <ExpandMoreIcon
                sx={{
                  transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
                  transition: 'transform 0.3s'
                }}
              />
            </IconButton>
            <Box sx={{ ml: 'auto', display: 'flex', gap: 1 }}>
              <IconButton
                size="small"
                onClick={handleEdit}
                title="Edit rule"
              >
                <EditIcon fontSize="small" />
              </IconButton>
              <IconButton
                size="small"
                color="error"
                onClick={() => setDeleteDialog(true)}
                title="Delete rule"
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Box>
          </CardActions>
        )}

        {isEditing && (
          <Box sx={{ px: 2, pb: 2 }}>
            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
              Conditions
            </Typography>
            <Stack spacing={1} sx={{ mb: 2 }}>
              {displayedRule.conditions.map((condition, idx) => (
                <Box key={idx} sx={{ display: 'flex', gap: 1, alignItems: 'flex-start' }}>
                  <TextField
                    fullWidth
                    value={condition}
                    onChange={(e) => handleArrayFieldChange('conditions', idx, e.target.value)}
                    variant="outlined"
                    size="small"
                    multiline
                  />
                  <Button
                    color="error"
                    size="small"
                    onClick={() => handleRemoveArrayItem('conditions', idx)}
                  >
                    Remove
                  </Button>
                </Box>
              ))}
              <Button
                size="small"
                onClick={() => handleAddArrayItem('conditions')}
              >
                + Add Condition
              </Button>
            </Stack>

            <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
              Expected Evidence
            </Typography>
            <Stack spacing={1} sx={{ mb: 2 }}>
              {displayedRule.expected_evidence.map((evidence, idx) => (
                <Box key={idx} sx={{ display: 'flex', gap: 1, alignItems: 'flex-start' }}>
                  <TextField
                    fullWidth
                    value={evidence}
                    onChange={(e) => handleArrayFieldChange('expected_evidence', idx, e.target.value)}
                    variant="outlined"
                    size="small"
                    multiline
                  />
                  <Button
                    color="error"
                    size="small"
                    onClick={() => handleRemoveArrayItem('expected_evidence', idx)}
                  >
                    Remove
                  </Button>
                </Box>
              ))}
              <Button
                size="small"
                onClick={() => handleAddArrayItem('expected_evidence')}
              >
                + Add Evidence
              </Button>
            </Stack>

            <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
              <Button
                startIcon={<CancelIcon />}
                onClick={handleCancel}
              >
                Cancel
              </Button>
              <Button
                startIcon={<SaveIcon />}
                variant="contained"
                onClick={handleSave}
              >
                Save
              </Button>
            </Box>
          </Box>
        )}

        <Collapse in={expanded && !isEditing} timeout="auto" unmountOnExit>
          <CardContent>
            <Divider sx={{ mb: 2 }} />

            <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
              Conditions
            </Typography>
            <Stack component="ul" spacing={0.5} sx={{ mb: 2, pl: 2 }}>
              {displayedRule.conditions.map((condition, idx) => (
                <Typography key={idx} component="li" variant="body2">
                  {condition}
                </Typography>
              ))}
            </Stack>

            <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 600 }}>
              Expected Evidence
            </Typography>
            <Stack component="ul" spacing={0.5} sx={{ pl: 2 }}>
              {displayedRule.expected_evidence.map((evidence, idx) => (
                <Typography key={idx} component="li" variant="body2">
                  {evidence}
                </Typography>
              ))}
            </Stack>
          </CardContent>
        </Collapse>
      </Card>

      <Dialog open={deleteDialog} onClose={() => setDeleteDialog(false)}>
        <DialogTitle>Delete Rule?</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{rule.title}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(false)}>Cancel</Button>
          <Button
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </>
  )
}
