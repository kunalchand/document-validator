import uuid

from app.core import get_logger
from app.providers.base import EmbeddingProvider
from app.providers.schemas import EmbeddingRequest, EmbeddingResponse

logger = get_logger(__name__)


class DummyEmbeddingProvider(EmbeddingProvider):
    """
    Placeholder embedding provider used until Phase 2 real embedding providers are added.
    Returns zero-valued vectors of the correct dimension.
    """

    def _validate_config(self) -> None:
        logger.info("DummyEmbeddingProvider initialized (Phase 2 placeholder)")

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        dim = self.embedding_dimension
        return EmbeddingResponse(
            embedding=[0.0] * dim,
            model=self.config.get("model", "dummy-embedding"),
            provider=self.provider_name,
            text_length=len(request.text),
            metadata={"is_placeholder": True, "request_id": str(uuid.uuid4())},
        )

    @property
    def provider_name(self) -> str:
        return "dummy"

    @property
    def embedding_dimension(self) -> int:
        return self.config.get("embedding_dim", 1536)
