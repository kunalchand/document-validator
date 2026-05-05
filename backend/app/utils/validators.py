from app.core import InvalidInputException

SUPPORTED_FILE_EXTENSIONS = ['.pdf', '.docx', '.doc']
SUPPORTED_MIME_TYPES = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']


def validate_file(filename: str, file_size: int, max_size_mb: int) -> None:
    """
    Validate file upload.

    Args:
        filename: Name of the uploaded file
        file_size: Size of file in bytes
        max_size_mb: Maximum allowed size in MB

    Raises:
        InvalidInputException: If validation fails
    """
    if not filename:
        raise InvalidInputException("File name is required")

    # Check file extension
    file_extension = ''.join(['.', filename.split('.')[-1]]).lower()
    if file_extension not in SUPPORTED_FILE_EXTENSIONS:
        raise InvalidInputException(
            f"Unsupported file type '{file_extension}'. Supported types: {', '.join(SUPPORTED_FILE_EXTENSIONS)}"
        )

    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise InvalidInputException(
            f"File size exceeds maximum of {max_size_mb}MB. Provided size: {file_size / (1024 * 1024):.2f}MB"
        )


def validate_text(text: str, max_length: int) -> None:
    """
    Validate text input.

    Args:
        text: Text input to validate
        max_length: Maximum allowed character length

    Raises:
        InvalidInputException: If validation fails
    """
    if not text or not text.strip():
        raise InvalidInputException("Text input cannot be empty")

    if len(text) > max_length:
        raise InvalidInputException(
            f"Text length exceeds maximum of {max_length} characters. Provided length: {len(text)}"
        )
