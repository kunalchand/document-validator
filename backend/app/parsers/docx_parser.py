import io
from typing import Union

from docx import Document

from app.parsers.base import DocumentParser
from app.core import get_logger
from app.core.exceptions import FileParseFailed

logger = get_logger(__name__)


class DOCXParser(DocumentParser):
    """Parser for DOCX documents using python-docx"""

    def parse(self, content: Union[bytes, str]) -> str:
        if not isinstance(content, bytes):
            raise FileParseFailed("DOCXParser expects bytes input", file_type="docx")

        try:
            doc = Document(io.BytesIO(content))
            paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]

            result = "\n\n".join(paragraphs)
            logger.debug(f"DOCX parsed: {len(paragraphs)} paragraphs, {len(result)} chars")
            return result

        except FileParseFailed:
            raise
        except Exception as e:
            logger.error(f"DOCX parsing failed: {e}")
            raise FileParseFailed(f"Failed to parse DOCX: {e}", file_type="docx")

    @property
    def supported_formats(self) -> list[str]:
        return ["docx", "doc"]
