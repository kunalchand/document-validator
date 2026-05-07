from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from app.providers.schemas import LLMRequest, LLMResponse, EmbeddingRequest, EmbeddingResponse


class LLMProvider(ABC):
    """
    Abstract base for Language Model providers.
    Concrete subclasses implement async generation; concurrency is handled
    by callers via asyncio.gather, so no batch_generate / sync variants are needed here.
    """

    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        self.api_key = api_key
        self.config = config or {}
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate provider configuration. Raise ValueError if invalid."""
        pass

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text from the LLM. Implementations should raise on API/network failure."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider identifier (e.g., 'anthropic', 'grok', 'ollama'). Used in LLMResponse metadata."""
        pass

    @property
    def max_concurrency(self) -> int:
        """
        Max number of simultaneous LLM requests the pipeline should issue.
        0 = unlimited (default for cloud providers).
        1 = serial (one at a time — correct for local Ollama which queues requests anyway).
        Override in concrete providers where the server can't truly parallelize.
        """
        return 0


class EmbeddingProvider(ABC):
    """
    Abstract base for Embedding providers.
    Used by Phase 2 (vector DB indexing); not exercised in Phase 1.
    """

    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        self.api_key = api_key
        self.config = config or {}
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        pass

    @abstractmethod
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def embedding_dimension(self) -> int:
        """Vector dimension produced by this provider — needed for vector DB schema."""
        pass
