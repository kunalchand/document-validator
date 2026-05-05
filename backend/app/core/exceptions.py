class DocumentValidatorException(Exception):
    """Base exception for Document Validator"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class InvalidInputException(DocumentValidatorException):
    """Raised when input validation fails"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class FileParseFailed(DocumentValidatorException):
    """Raised when file parsing fails"""
    def __init__(self, message: str, file_type: str):
        super().__init__(f"Failed to parse {file_type}: {message}", status_code=422)


class ExtractionFailed(DocumentValidatorException):
    """Raised when rule extraction fails"""
    def __init__(self, message: str):
        super().__init__(f"Rules extraction failed: {message}", status_code=500)


class AuditFailed(DocumentValidatorException):
    """Raised when audit process fails"""
    def __init__(self, message: str):
        super().__init__(f"Audit process failed: {message}", status_code=500)
