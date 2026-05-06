from typing import Optional, Dict, Any
from enum import Enum

from app.core import get_logger
from app.providers.base import LLMProvider, EmbeddingProvider
from app.providers.dummy_provider import DummyEmbeddingProvider
from app.providers.anthropic_provider import AnthropicLLMProvider
from app.providers.grok_provider import GrokLLMProvider
from app.providers.ollama_provider import OllamaLLMProvider

logger = get_logger(__name__)


class ProviderType(str, Enum):
    """Supported LLM/Embedding provider types"""
    ANTHROPIC = "anthropic"
    GROK = "grok"
    OLLAMA = "ollama"
    DUMMY = "dummy"     # embedding placeholder only — not valid for LLM
    OPENAI = "openai"   # reserved for future use
    GOOGLE = "google"   # reserved for future use


class ProviderFactory:
    """
    Factory for creating LLM and Embedding provider instances.
    Implements the factory pattern for provider selection.
    """

    _llm_providers = {
        ProviderType.ANTHROPIC: AnthropicLLMProvider,
        ProviderType.GROK: GrokLLMProvider,
        ProviderType.OLLAMA: OllamaLLMProvider,
    }

    _embedding_providers = {
        ProviderType.DUMMY: DummyEmbeddingProvider,
        # Real embedding providers added in Phase 2
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
            available = [p.value for p in cls._llm_providers]
            raise ValueError(
                f"'{provider_type}' is not a valid LLM provider. "
                f"Set LLM_PROVIDER to one of: {', '.join(available)}"
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
