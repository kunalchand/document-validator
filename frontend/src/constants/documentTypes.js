export const DOCUMENT_TYPES = {
  FILE: 'file',
  TEXT: 'text'
}

export const FILE_TYPES = {
  PDF: 'application/pdf',
  DOCX: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}

export const FILE_EXTENSIONS = {
  PDF: '.pdf',
  DOCX: '.docx'
}

export const SUPPORTED_FORMATS = [
  { type: FILE_TYPES.PDF, extension: FILE_EXTENSIONS.PDF, label: 'PDF' },
  { type: FILE_TYPES.DOCX, extension: FILE_EXTENSIONS.DOCX, label: 'DOCX' }
]

export const MAX_FILE_SIZE_MB = 10
export const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
