import React from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Alert
} from '@mui/material'
import WarningIcon from '@mui/icons-material/Warning'

export const ConfirmationDialog = ({
  open,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  onConfirm,
  onCancel,
  severity = 'warning',
  confirmColor = 'error',
  loading = false
}) => {
  const getSeverityIcon = () => {
    switch (severity) {
      case 'warning':
        return <WarningIcon sx={{ color: 'warning.main', mr: 1 }} />
      case 'error':
        return <WarningIcon sx={{ color: 'error.main', mr: 1 }} />
      case 'info':
        return null
      default:
        return null
    }
  }

  return (
    <Dialog
      open={open}
      onClose={onCancel}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2
        }
      }}
    >
      <DialogTitle sx={{ pb: 1 }}>
        <Typography
          variant="h6"
          sx={{ display: 'flex', alignItems: 'center', fontWeight: 600 }}
        >
          {getSeverityIcon()}
          {title}
        </Typography>
      </DialogTitle>

      <DialogContent sx={{ pt: 2 }}>
        <Typography variant="body2" color="textSecondary" paragraph>
          {message}
        </Typography>

        {severity !== 'info' && (
          <Alert severity={severity} sx={{ mt: 2 }}>
            This action cannot be easily undone.
          </Alert>
        )}
      </DialogContent>

      <DialogActions sx={{ p: 2, gap: 1 }}>
        <Button
          onClick={onCancel}
          disabled={loading}
        >
          {cancelText}
        </Button>
        <Button
          onClick={onConfirm}
          variant="contained"
          color={confirmColor}
          disabled={loading}
          autoFocus
        >
          {loading ? 'Processing...' : confirmText}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
