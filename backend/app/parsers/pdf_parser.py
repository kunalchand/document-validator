import io
from typing import Union

from PyPDF2 import PdfReader

from app.parsers.base import DocumentParser
from app.core import get_logger
from app.core.exceptions import FileParseFailed

logger = get_logger(__name__)


class PDFParser(DocumentParser):
    """Parser for PDF documents using PyPDF2"""

    def parse(self, content: Union[bytes, str]) -> str:
        if not isinstance(content, bytes):
            raise FileParseFailed("PDFParser expects bytes input", file_type="pdf")

        try:
            reader = PdfReader(io.BytesIO(content))
            pages_text = []

            for page in reader.pages:
                text = page.extract_text()
                if text and text.strip():
                    pages_text.append(text.strip())

            result = "\n\n".join(pages_text)
            logger.debug(f"PDF parsed: {len(reader.pages)} pages, {len(result)} chars")
            return result

        except FileParseFailed:
            raise
        except Exception as e:
            logger.error(f"PDF parsing failed: {e}")
            raise FileParseFailed(f"Failed to parse PDF: {e}", file_type="pdf")

    @property
    def supported_formats(self) -> list[str]:
        return ["pdf"]
