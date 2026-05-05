# Provider Abstraction Layer

This module implements a provider-agnostic abstraction layer for LLM and embedding providers. It allows seamless switching between different AI/ML service providers (OpenAI, Anthropic, Google, etc.) without changing application code.

## Architecture

### Design Pattern: Abstract Factory

The provider system uses abstract base classes and the factory pattern to:
- **Decouple** application code from specific provider implementations
- **Enable** runtime provider switching via configuration
- **Facilitate** testing with mock implementations
- **Support** easy addition of new providers

### Core Components

#### 1. Abstract Base Classes (`base.py`)

Define interfaces that all providers must implement:

- **`LLMProvider`** - Interface for language model operations
  - `generate()` - Async text generation
  - `generate_sync()` - Synchronous text generation
  - `batch_generate()` - Efficient batch processing
  - `provider_name` - Provider identifier (read-only)
  - `available_models` - List of supported models (read-only)

- **`EmbeddingProvider`** - Interface for text embeddings
  - `embed()` - Async embedding generation
  - `embed_sync()` - Synchronous embedding generation
  - `batch_embed()` - Batch embedding processing
  - `provider_name` - Provider identifier (read-only)
  - `embedding_dimension` - Vector dimension (read-only)
  - `available_models` - List of supported models (read-only)

#### 2. Standardized Data Models (`schemas.py`)

Pydantic models for type-safe communication:

- **`LLMRequest`** - Request to LLM
  - `prompt` - The input prompt
  - `model` - Specific model to use (optional)
  - `temperature` - Response randomness (0-1)
  - `max_tokens` - Output length limit
  - `system_prompt` - System message/context
  - `metadata` - Additional data

- **`LLMResponse`** - Response from LLM
  - `content` - Generated text
  - `model` - Model that generated response
  - `provider` - Provider name
  - `tokens_used` - Token consumption
  - `metadata` - Additional data

- **`EmbeddingRequest`** & **`EmbeddingResponse`** - Similar structure for embeddings

#### 3. Concrete Implementations

##### Dummy Provider (`dummy_provider.py`)
- **Purpose**: Development, testing, demo without API calls
- **Returns**: Predictable mock responses
- **Use Case**: Unit tests, UI development, proof-of-concept

##### OpenAI Provider (Planned)
- GPT-4, GPT-3.5-turbo, text-embedding-3-small, text-embedding-3-large

##### Anthropic Provider (Planned)
- Claude family models

##### Google Provider (Planned)
- Gemini family, text-embedding-004

##### Additional Providers (Extensible)
- xAI Grok, custom providers, etc.

#### 4. Factory Pattern (`factory.py`)

**`ProviderFactory`** - Creates provider instances

```python
# Create a provider
provider = ProviderFactory.create_llm_provider(
    provider_type="openai",
    api_key="sk-...",
    config={"model": "gpt-4"}
)

# Register custom providers at runtime
ProviderFactory.register_llm_provider(
    ProviderType.CUSTOM,
    CustomLLMProvider
)
```

## Usage

### Configuration

Set provider via environment variables:

```env
# Use dummy provider for development
LLM_PROVIDER=dummy
EMBEDDING_PROVIDER=dummy

# Switch to OpenAI in production
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4

EMBEDDING_PROVIDER=openai
EMBEDDING_API_KEY=sk-...
EMBEDDING_MODEL=text-embedding-3-small
```

### In Code

```python
from app.providers import ProviderFactory, LLMRequest

# Create provider (config drives which one)
provider = ProviderFactory.create_llm_provider(
    provider_type=settings.llm_provider,
    api_key=settings.llm_api_key,
    config={"model": settings.llm_model}
)

# Use provider (same code works with any implementation)
request = LLMRequest(
    prompt="Extract key information from this text...",
    temperature=0.7,
    max_tokens=500
)

response = await provider.generate(request)
print(response.content)  # Works the same way regardless of provider
```

## Adding a New Provider

See `PROVIDER_TEMPLATE.md` for complete instructions.

Quick summary:
1. Create class inheriting from `LLMProvider` or `EmbeddingProvider`
2. Implement all abstract methods
3. Register in factory
4. Update configuration

## Benefits

### 1. **Flexibility**
- Switch providers with configuration change
- No code changes needed
- Test multiple providers easily

### 2. **Maintainability**
- Single interface for all providers
- Provider-specific logic isolated
- Easy to deprecate old providers

### 3. **Testability**
- Dummy provider for unit tests
- Mock responses without API calls
- Deterministic test behavior

### 4. **Extensibility**
- Add new providers without modifying core
- Runtime provider registration
- Custom provider support

### 5. **Cost Optimization**
- Use cheaper providers for some tasks
- Switch based on performance needs
- A/B test different providers

## Supported Providers

| Provider | LLM | Embedding | Status |
|----------|-----|-----------|--------|
| Dummy | ✓ | ✓ | Ready |
| OpenAI | 🔲 | 🔲 | Planned |
| Anthropic | 🔲 | 🔲 | Planned |
| Google | 🔲 | 🔲 | Planned |
| xAI Grok | 🔲 | 🔲 | Planned |

✓ = Implemented, 🔲 = Planned, ❌ = Not supported

## Error Handling

Providers raise domain-specific exceptions:
- `ValueError` - Configuration errors
- `Exception` - API/connection errors
- Provider-specific exceptions if needed

Applications should catch exceptions and handle gracefully.

## Performance Considerations

- Async methods recommended for concurrent requests
- Batch methods for multiple requests
- Caching/memoization at application level
- Rate limiting handled by provider implementations

## Future Enhancements

- [ ] Caching layer for responses
- [ ] Fallback provider chaining
- [ ] Cost tracking per provider
- [ ] Performance metrics/monitoring
- [ ] Fine-tuning support
- [ ] Vision/multimodal support
