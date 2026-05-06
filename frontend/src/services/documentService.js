import apiClient from './apiClient'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

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

  extractRulesStream: async (payload, onEvent) => {
    const formData = new FormData()
    formData.append(payload.type === 'file' ? 'file' : 'text', payload.content)

    const response = await fetch(`${API_BASE_URL}/api/v1/extract-rules-stream`, {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    const processLine = (line) => {
      if (line.startsWith('data: ')) {
        try {
          const event = JSON.parse(line.slice(6))
          onEvent(event)
        } catch (e) {
          console.error('Failed to parse SSE event:', e)
        }
      }
    }

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        lines.forEach(processLine)
      }

      buffer += decoder.decode()
      if (buffer) processLine(buffer)
    } finally {
      reader.releaseLock()
    }
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
