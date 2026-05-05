import apiClient from './apiClient'

export const documentService = {
  extractRules: async (document) => {
    const formData = new FormData()
    formData.append('file', document)

    return apiClient.post('/extract-rules', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  extractRulesFromText: async (text) => {
    return apiClient.post('/extract-rules', {
      text
    })
  },

  auditDocument: async (document, rules) => {
    const formData = new FormData()
    formData.append('file', document)
    formData.append('rules', JSON.stringify(rules))

    return apiClient.post('/audit', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  auditDocumentWithText: async (text, rules) => {
    return apiClient.post('/audit', {
      text,
      rules
    })
  }
}
