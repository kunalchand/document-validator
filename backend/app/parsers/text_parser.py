from typing import Union

from app.parsers.base import DocumentParser
from app.core import get_logger

logger = get_logger(__name__)


class TextParser(DocumentParser):
    """Passthrough parser for plain text input"""

    def parse(self, content: Union[bytes, str]) -> str:
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="replace")

        result = content.strip()
        logger.debug(f"Text input passed through: {len(result)} chars")
        return result

    @property
    def supported_formats(self) -> list[str]:
        return ["txt", "text"]
