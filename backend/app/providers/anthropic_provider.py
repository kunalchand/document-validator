import asyncio
from typing import Optional, Dict, Any

from anthropic import AsyncAnthropic, Anthropic, APIStatusError, APIConnectionError

from app.core import get_logger
from app.providers.base import LLMProvider
from app.providers.schemas import LLMRequest, LLMResponse

logger = get_logger(__name__)

_DEFAULT_MODEL = "claude-haiku-4-5-20251001"
_AVAILABLE_MODELS = [
    "claude-haiku-4-5-20251001",
    "claude-sonnet-4-6",
    "claude-opus-4-7",
]


class AnthropicLLMProvider(LLMProvider):
    """
    Anthropic Claude provider.
    Uses the official anthropic SDK for both async and sync calls.
    """

    def _validate_config(self) -> None:
        if not self.api_key:
            raise ValueError("Anthropic API key is required (LLM_API_KEY)")
        self._async_client = AsyncAnthropic(api_key=self.api_key)
        self._sync_client = Anthropic(api_key=self.api_key)
        logger.info(f"AnthropicLLMProvider initialized: model={self._model}")

    @property
    def _model(self) -> str:
        return self.config.get("model", _DEFAULT_MODEL)

    def _build_kwargs(self, request: LLMRequest) -> dict:
        kwargs: Dict[str, Any] = {
            "model": request.model or self._model,
            "messages": [{"role": "user", "content": request.prompt}],
            "max_tokens": request.max_tokens or 4096,
            "temperature": request.temperature,
        }
        if request.system_prompt:
            kwargs["system"] = request.system_prompt
        return kwargs

    def _to_response(self, raw, model: str) -> LLMResponse:
        return LLMResponse(
            content=raw.content[0].text,
            model=raw.model,
            provider=self.provider_name,
            tokens_used=raw.usage.input_tokens + raw.usage.output_tokens,
            metadata={"stop_reason": raw.stop_reason},
        )

    async def generate(self, request: LLMRequest) -> LLMResponse:
        try:
            raw = await self._async_client.messages.create(**self._build_kwargs(request))
            return self._to_response(raw, request.model or self._model)
        except APIStatusError as e:
            logger.error(f"Anthropic API error {e.status_code}: {e.message}")
            raise
        except APIConnectionError as e:
            logger.error(f"Anthropic connection error: {e}")
            raise

    def generate_sync(self, request: LLMRequest) -> LLMResponse:
        try:
            raw = self._sync_client.messages.create(**self._build_kwargs(request))
            return self._to_response(raw, request.model or self._model)
        except APIStatusError as e:
            logger.error(f"Anthropic API error {e.status_code}: {e.message}")
            raise
        except APIConnectionError as e:
            logger.error(f"Anthropic connection error: {e}")
            raise

    async def batch_generate(self, requests: list[LLMRequest]) -> list[LLMResponse]:
        return list(await asyncio.gather(*[self.generate(r) for r in requests]))

    @property
    def provider_name(self) -> str:
        return "anthropic"

    @property
    def available_models(self) -> list[str]:
        return _AVAILABLE_MODELS
