import json
from typing import Optional, Dict, Any
import uuid

from app.core import get_logger
from app.providers.base import LLMProvider, EmbeddingProvider
from app.providers.schemas import LLMRequest, LLMResponse, EmbeddingRequest, EmbeddingResponse

logger = get_logger(__name__)

_DUMMY_EXTRACTION_RULES = json.dumps([
    {
        "title": "Employee Background Verification",
        "description": "All employees must undergo a comprehensive background check prior to employment commencement.",
        "conditions": [
            "Background check must be completed within 30 days of offer acceptance",
            "Check must be performed by an accredited third-party vendor",
        ],
        "expected_evidence": [
            "Signed background check consent form",
            "Background check report from accredited vendor",
        ],
        "severity": "high",
        "section": "Section 2: Hiring Procedures",
    },
    {
        "title": "Data Confidentiality Agreement",
        "description": "Every employee must sign a data confidentiality and non-disclosure agreement before their first day.",
        "conditions": [
            "Agreement must be signed before first day of work",
            "Agreement must cover all company intellectual property",
        ],
        "expected_evidence": [
            "Signed confidentiality agreement on file",
            "Date-stamped acknowledgement record",
        ],
        "severity": "high",
        "section": "Section 3: Employment Agreements",
    },
    {
        "title": "Annual Compliance Training",
        "description": "All employees must complete mandatory compliance training at least once per calendar year.",
        "conditions": [
            "Training must be completed by December 31st of each year",
            "Minimum passing score of 80% required",
        ],
        "expected_evidence": [
            "Training completion certificate",
            "Assessment score record",
        ],
        "severity": "medium",
        "section": "Section 5: Training Requirements",
    },
])


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
        """Generate a mock response; returns extraction JSON when prompt requests rules"""
        prompt_lower = request.prompt.lower()
        is_extraction = (
            "extract" in prompt_lower
            and any(kw in prompt_lower for kw in ("rule", "compliance", "requirement"))
        )
        content = _DUMMY_EXTRACTION_RULES if is_extraction else (
            "This is a dummy response for testing. No real LLM was called."
        )
        return LLMResponse(
            content=content,
            model=self.config.get("model", "dummy-model"),
            provider=self.provider_name,
            tokens_used=100,
            metadata={"is_dummy": True, "request_id": str(uuid.uuid4())},
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
