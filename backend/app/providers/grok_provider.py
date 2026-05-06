import asyncio
from typing import Optional

from openai import AsyncOpenAI, OpenAI, APIStatusError, APIConnectionError

from app.core import get_logger
from app.providers.base import LLMProvider
from app.providers.schemas import LLMRequest, LLMResponse

logger = get_logger(__name__)

_GROK_BASE_URL = "https://api.x.ai/v1"
_DEFAULT_MODEL = "grok-3-mini"
_AVAILABLE_MODELS = [
    "grok-3-mini",
    "grok-3",
    "grok-2",
]


class GrokLLMProvider(LLMProvider):
    """
    xAI Grok provider.
    Grok exposes an OpenAI-compatible API, so we use the openai SDK
    pointed at https://api.x.ai/v1 with the Grok API key.
    """

    def _validate_config(self) -> None:
        if not self.api_key:
            raise ValueError("Grok API key is required (LLM_API_KEY)")
        self._async_client = AsyncOpenAI(api_key=self.api_key, base_url=_GROK_BASE_URL)
        self._sync_client = OpenAI(api_key=self.api_key, base_url=_GROK_BASE_URL)
        logger.info(f"GrokLLMProvider initialized: model={self._model}")

    @property
    def _model(self) -> str:
        return self.config.get("model", _DEFAULT_MODEL)

    def _build_messages(self, request: LLMRequest) -> list:
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})
        return messages

    def _to_response(self, raw) -> LLMResponse:
        return LLMResponse(
            content=raw.choices[0].message.content,
            model=raw.model,
            provider=self.provider_name,
            tokens_used=raw.usage.total_tokens if raw.usage else None,
            metadata={"finish_reason": raw.choices[0].finish_reason},
        )

    async def generate(self, request: LLMRequest) -> LLMResponse:
        try:
            raw = await self._async_client.chat.completions.create(
                model=request.model or self._model,
                messages=self._build_messages(request),
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            return self._to_response(raw)
        except APIStatusError as e:
            logger.error(f"Grok API error {e.status_code}: {e.message}")
            raise
        except APIConnectionError as e:
            logger.error(f"Grok connection error: {e}")
            raise

    def generate_sync(self, request: LLMRequest) -> LLMResponse:
        try:
            raw = self._sync_client.chat.completions.create(
                model=request.model or self._model,
                messages=self._build_messages(request),
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
            return self._to_response(raw)
        except APIStatusError as e:
            logger.error(f"Grok API error {e.status_code}: {e.message}")
            raise
        except APIConnectionError as e:
            logger.error(f"Grok connection error: {e}")
            raise

    async def batch_generate(self, requests: list[LLMRequest]) -> list[LLMResponse]:
        return list(await asyncio.gather(*[self.generate(r) for r in requests]))

    @property
    def provider_name(self) -> str:
        return "grok"

    @property
    def available_models(self) -> list[str]:
        return _AVAILABLE_MODELS
