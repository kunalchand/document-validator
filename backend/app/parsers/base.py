from abc import ABC, abstractmethod
from typing import Union

from app.core import get_logger

logger = get_logger(__name__)


class DocumentParser(ABC):
    """Abstract base class for document parsers"""

    @abstractmethod
    def parse(self, content: Union[bytes, str]) -> str:
        """Parse document content and return plain text"""
        ...

    @property
    @abstractmethod
    def supported_formats(self) -> list[str]:
        """List of supported file extensions"""
        ...
