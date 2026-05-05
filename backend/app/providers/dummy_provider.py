from typing import Optional, Dict, Any
import uuid

from app.core import get_logger
from app.providers.base import LLMProvider, EmbeddingProvider
from app.providers.schemas import LLMRequest, LLMResponse, EmbeddingRequest, EmbeddingResponse

logger = get_logger(__name__)


class DummyLLMProvider(LLMProvider):
    """
    Dummy LLM provider for development and testing.
    Returns mock responses without making actual API calls.
    """

    def _validate_config(self) -> None:
        """Dummy validation - always passes"""
        logger.info("DummyLLMProvider initialized (no real API calls)")

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Generate dummy response"""
        return self._generate_dummy_response(request)

    def generate_sync(self, request: LLMRequest) -> LLMResponse:
        """Generate dummy response synchronously"""
        return self._generate_dummy_response(request)

    async def batch_generate(self, requests: list[LLMRequest]) -> list[LLMResponse]:
        """Generate dummy responses for batch"""
        return [self._generate_dummy_response(req) for req in requests]

    def _generate_dummy_response(self, request: LLMRequest) -> LLMResponse:
        """Generate a mock response"""
        return LLMResponse(
            content="This is a dummy response for testing. No real LLM was called.",
            model=self.config.get("model", "dummy-model"),
            provider=self.provider_name,
            tokens_used=100,
            metadata={"is_dummy": True, "request_id": str(uuid.uuid4())}
        )

    @property
    def provider_name(self) -> str:
        return "dummy"

    @property
    def available_models(self) -> list[str]:
        return ["dummy-model", "dummy-model-v2"]


class DummyEmbeddingProvider(EmbeddingProvider):
    """
    Dummy embedding provider for development and testing.
    Returns mock embeddings without making actual API calls.
    """

    def _validate_config(self) -> None:
        """Dummy validation - always passes"""
        logger.info("DummyEmbeddingProvider initialized (no real API calls)")

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate dummy embedding"""
        return self._generate_dummy_embedding(request)

    def embed_sync(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate dummy embedding synchronously"""
        return self._generate_dummy_embedding(request)

    async def batch_embed(self, requests: list[EmbeddingRequest]) -> list[EmbeddingResponse]:
        """Generate dummy embeddings for batch"""
        return [self._generate_dummy_embedding(req) for req in requests]

    def _generate_dummy_embedding(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate a mock embedding"""
        # Generate a dummy embedding vector based on text length
        dim = self.embedding_dimension
        dummy_vector = [float(i % 10) / 10.0 for i in range(dim)]

        return EmbeddingResponse(
            embedding=dummy_vector,
            model=self.config.get("model", "dummy-embedding"),
            provider=self.provider_name,
            text_length=len(request.text),
            metadata={"is_dummy": True, "request_id": str(uuid.uuid4())}
        )

    @property
    def provider_name(self) -> str:
        return "dummy"

    @property
    def embedding_dimension(self) -> int:
        return self.config.get("embedding_dim", 1536)

    @property
    def available_models(self) -> list[str]:
        return ["dummy-embedding", "dummy-embedding-v2"]
