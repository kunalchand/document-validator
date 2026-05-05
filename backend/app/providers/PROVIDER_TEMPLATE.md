# Adding New LLM/Embedding Providers

This guide explains how to add support for a new LLM or embedding provider to the system.

## Architecture Overview

The provider system uses:
- **Abstract Base Classes** (`LLMProvider`, `EmbeddingProvider`) - Define the interface
- **Concrete Implementations** - Implement the interface for specific providers
- **Factory Pattern** (`ProviderFactory`) - Create provider instances

## Adding a New LLM Provider

### Step 1: Create the Provider Class

Create a new file `app/providers/openai_provider.py`:

```python
from typing import Optional, Dict, Any
from app.providers.base import LLMProvider
from app.providers.schemas import LLMRequest, LLMResponse
from app.core import get_logger

logger = get_logger(__name__)


class OpenAILLMProvider(LLMProvider):
    """OpenAI LLM provider implementation"""

    def _validate_config(self) -> None:
        """Validate OpenAI configuration"""
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        if "model" not in self.config:
            raise ValueError("Model must be specified in config")
        logger.info(f"OpenAI provider initialized with model: {self.config['model']}")

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate text using OpenAI API"""
        # TODO: Implement actual OpenAI API call
        # Use openai client library
        pass

    def generate_sync(self, request: LLMRequest) -> LLMResponse:
        """Generate text synchronously"""
        # Synchronous wrapper around async method
        pass

    async def batch_generate(self, requests: list[LLMRequest]) -> list[LLMResponse]:
        """Batch generation using OpenAI"""
        pass

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def available_models(self) -> list[str]:
        return [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
        ]
```

### Step 2: Register the Provider

In `app/providers/factory.py`, add to the imports and factory:

```python
from app.providers.openai_provider import OpenAILLMProvider

# In ProviderFactory class:
_llm_providers = {
    ProviderType.DUMMY: DummyLLMProvider,
    ProviderType.OPENAI: OpenAILLMProvider,  # Add this line
}
```

### Step 3: Update Configuration

In `.env.example` and `.env`:

```env
LLM_PROVIDER=openai
LLM_API_KEY=sk-your-openai-api-key
LLM_MODEL=gpt-4
```

## Adding a New Embedding Provider

Follow the same pattern but inherit from `EmbeddingProvider`:

```python
class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider"""

    def _validate_config(self) -> None:
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        # Implement embedding logic
        pass

    def embed_sync(self, request: EmbeddingRequest) -> EmbeddingResponse:
        # Synchronous wrapper
        pass

    async def batch_embed(self, requests: list[EmbeddingRequest]) -> list[EmbeddingResponse]:
        # Batch embedding
        pass

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def embedding_dimension(self) -> int:
        return 1536  # OpenAI's default embedding dimension

    @property
    def available_models(self) -> list[str]:
        return [
            "text-embedding-3-small",
            "text-embedding-3-large",
        ]
```

## Using Multiple Providers

Switch providers by changing configuration:

```env
# Use OpenAI for LLM, Gemini for embeddings
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=google
```

## Provider Interface Contract

Every provider MUST implement:

### LLMProvider
- `_validate_config()` - Validate configuration
- `async generate()` - Single async generation
- `generate_sync()` - Single synchronous generation
- `async batch_generate()` - Batch generation
- `provider_name` property - Return provider identifier
- `available_models` property - List available models

### EmbeddingProvider
- `_validate_config()` - Validate configuration
- `async embed()` - Single async embedding
- `embed_sync()` - Single synchronous embedding
- `async batch_embed()` - Batch embedding
- `provider_name` property - Return provider identifier
- `embedding_dimension` property - Vector dimension
- `available_models` property - List available models

## Testing a New Provider

```python
from app.providers import ProviderFactory, LLMRequest

# Create provider instance
provider = ProviderFactory.create_llm_provider(
    provider_type="openai",
    api_key="sk-your-key",
    config={"model": "gpt-4"}
)

# Use it
request = LLMRequest(
    prompt="Hello, world!",
    temperature=0.7
)
response = await provider.generate(request)
print(response.content)
```

## Supported Provider Types

Currently planned:
- `dummy` - For testing (no API calls)
- `openai` - OpenAI GPT models
- `anthropic` - Claude models
- `google` - Gemini models
- `grok` - xAI Grok models

Add more as needed by following the pattern above.
