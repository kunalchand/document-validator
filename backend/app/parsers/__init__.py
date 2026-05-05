from app.parsers.base import DocumentParser
from app.parsers.pdf_parser import PDFParser
from app.parsers.docx_parser import DOCXParser
from app.parsers.text_parser import TextParser

__all__ = ["DocumentParser", "PDFParser", "DOCXParser", "TextParser"]
