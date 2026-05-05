from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from app.providers.schemas import LLMRequest, LLMResponse, EmbeddingRequest, EmbeddingResponse


class LLMProvider(ABC):
    """
    Abstract base class for Language Model providers.
    Defines the interface that all LLM providers must implement.
    """

    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the LLM provider.

        Args:
            api_key: API key for authentication with the provider
            config: Provider-specific configuration (model name, endpoints, etc.)
        """
        self.api_key = api_key
        self.config = config or {}
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate provider configuration. Raise exception if invalid."""
        pass

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """
        Generate text using the LLM.

        Args:
            request: LLMRequest containing prompt and parameters

        Returns:
            LLMResponse with the generated content

        Raises:
            Exception: If API call fails or provider is misconfigured
        """
        pass

    @abstractmethod
    def generate_sync(self, request: LLMRequest) -> LLMResponse:
        """
        Generate text synchronously (blocking).

        Args:
            request: LLMRequest containing prompt and parameters

        Returns:
            LLMResponse with the generated content
        """
        pass

    @abstractmethod
    async def batch_generate(self, requests: list[LLMRequest]) -> list[LLMResponse]:
        """
        Generate text for multiple requests efficiently.

        Args:
            requests: List of LLMRequest objects

        Returns:
            List of LLMResponse objects in same order as input
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the provider (e.g., 'openai', 'anthropic')"""
        pass

    @property
    @abstractmethod
    def available_models(self) -> list[str]:
        """Return list of available models for this provider"""
        pass


class EmbeddingProvider(ABC):
    """
    Abstract base class for Embedding providers.
    Defines the interface for generating text embeddings.
    """

    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the embedding provider.

        Args:
            api_key: API key for authentication
            config: Provider-specific configuration
        """
        self.api_key = api_key
        self.config = config or {}
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """Validate provider configuration."""
        pass

    @abstractmethod
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """
        Generate embedding for text.

        Args:
            request: EmbeddingRequest containing text and parameters

        Returns:
            EmbeddingResponse with the embedding vector
        """
        pass

    @abstractmethod
    def embed_sync(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embedding synchronously."""
        pass

    @abstractmethod
    async def batch_embed(self, requests: list[EmbeddingRequest]) -> list[EmbeddingResponse]:
        """Generate embeddings for multiple texts efficiently."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of the provider"""
        pass

    @property
    @abstractmethod
    def embedding_dimension(self) -> int:
        """Return the dimension of embeddings produced by this provider"""
        pass

    @property
    @abstractmethod
    def available_models(self) -> list[str]:
        """Return list of available embedding models"""
        pass
