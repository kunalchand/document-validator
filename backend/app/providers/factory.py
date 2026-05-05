from typing import Optional, Dict, Any
from enum import Enum

from app.core import get_logger
from app.providers.base import LLMProvider, EmbeddingProvider
from app.providers.dummy_provider import DummyLLMProvider, DummyEmbeddingProvider

logger = get_logger(__name__)


class ProviderType(str, Enum):
    """Supported LLM provider types"""
    DUMMY = "dummy"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROK = "grok"


class ProviderFactory:
    """
    Factory for creating LLM and Embedding provider instances.
    Implements the factory pattern for provider selection.
    """

    _llm_providers = {
        ProviderType.DUMMY: DummyLLMProvider,
        # TODO: Add concrete implementations
        # ProviderType.OPENAI: OpenAILLMProvider,
        # ProviderType.ANTHROPIC: AnthropicLLMProvider,
        # ProviderType.GOOGLE: GoogleLLMProvider,
    }

    _embedding_providers = {
        ProviderType.DUMMY: DummyEmbeddingProvider,
        # TODO: Add concrete implementations
        # ProviderType.OPENAI: OpenAIEmbeddingProvider,
        # ProviderType.GOOGLE: GoogleEmbeddingProvider,
    }

    @classmethod
    def create_llm_provider(
        cls,
        provider_type: str,
        api_key: str,
        config: Optional[Dict[str, Any]] = None
    ) -> LLMProvider:
        """
        Create an LLM provider instance.

        Args:
            provider_type: Type of provider (see ProviderType enum)
            api_key: API key for the provider
            config: Provider-specific configuration

        Returns:
            Instance of the specified LLM provider

        Raises:
            ValueError: If provider type is not supported
        """
        try:
            provider_enum = ProviderType(provider_type.lower())
        except ValueError:
            raise ValueError(
                f"Unsupported LLM provider: {provider_type}. "
                f"Supported: {', '.join([p.value for p in ProviderType])}"
            )

        provider_class = cls._llm_providers.get(provider_enum)
        if not provider_class:
            raise ValueError(
                f"LLM provider '{provider_type}' is not yet implemented. "
                f"Available: {list(cls._llm_providers.keys())}"
            )

        logger.info(f"Creating LLM provider: {provider_type}")
        return provider_class(api_key=api_key, config=config or {})

    @classmethod
    def create_embedding_provider(
        cls,
        provider_type: str,
        api_key: str,
        config: Optional[Dict[str, Any]] = None
    ) -> EmbeddingProvider:
        """
        Create an embedding provider instance.

        Args:
            provider_type: Type of provider
            api_key: API key for the provider
            config: Provider-specific configuration

        Returns:
            Instance of the specified embedding provider

        Raises:
            ValueError: If provider type is not supported
        """
        try:
            provider_enum = ProviderType(provider_type.lower())
        except ValueError:
            raise ValueError(
                f"Unsupported embedding provider: {provider_type}. "
                f"Supported: {', '.join([p.value for p in ProviderType])}"
            )

        provider_class = cls._embedding_providers.get(provider_enum)
        if not provider_class:
            raise ValueError(
                f"Embedding provider '{provider_type}' is not yet implemented. "
                f"Available: {list(cls._embedding_providers.keys())}"
            )

        logger.info(f"Creating embedding provider: {provider_type}")
        return provider_class(api_key=api_key, config=config or {})

    @classmethod
    def register_llm_provider(
        cls,
        provider_type: ProviderType,
        provider_class: type[LLMProvider]
    ) -> None:
        """
        Register a new LLM provider implementation.
        Allows runtime registration of custom providers.

        Args:
            provider_type: The provider type enum
            provider_class: The provider class (must inherit from LLMProvider)
        """
        if not issubclass(provider_class, LLMProvider):
            raise TypeError(f"{provider_class} must inherit from LLMProvider")
        cls._llm_providers[provider_type] = provider_class
        logger.info(f"Registered LLM provider: {provider_type.value}")

    @classmethod
    def register_embedding_provider(
        cls,
        provider_type: ProviderType,
        provider_class: type[EmbeddingProvider]
    ) -> None:
        """
        Register a new embedding provider implementation.

        Args:
            provider_type: The provider type enum
            provider_class: The provider class (must inherit from EmbeddingProvider)
        """
        if not issubclass(provider_class, EmbeddingProvider):
            raise TypeError(f"{provider_class} must inherit from EmbeddingProvider")
        cls._embedding_providers[provider_type] = provider_class
        logger.info(f"Registered embedding provider: {provider_type.value}")

    @classmethod
    def list_available_llm_providers(cls) -> list[str]:
        """Return list of available LLM providers"""
        return list(cls._llm_providers.keys())

    @classmethod
    def list_available_embedding_providers(cls) -> list[str]:
        """Return list of available embedding providers"""
        return list(cls._embedding_providers.keys())
