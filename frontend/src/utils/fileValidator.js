import { FILE_TYPES, MAX_FILE_SIZE_BYTES } from '../constants/documentTypes'

export const validateFile = (file) => {
  const errors = []

  if (!file) {
    errors.push('No file selected')
    return { valid: false, errors }
  }

  const supportedTypes = Object.values(FILE_TYPES)
  if (!supportedTypes.includes(file.type)) {
    errors.push(`Unsupported file type. Supported: ${supportedTypes.join(', ')}`)
  }

  if (file.size > MAX_FILE_SIZE_BYTES) {
    errors.push(`File size exceeds maximum of 10MB`)
  }

  return {
    valid: errors.length === 0,
    errors
  }
}

export const validateText = (text) => {
  const errors = []

  if (!text || text.trim().length === 0) {
    errors.push('Text input cannot be empty')
  }

  if (text && text.length > 50000) {
    errors.push('Text input exceeds maximum length of 50,000 characters')
  }

  return {
    valid: errors.length === 0,
    errors
  }
}
