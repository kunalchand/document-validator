from typing import Dict, Any

from anthropic import AsyncAnthropic, APIStatusError, APIConnectionError

from app.core import get_logger
from app.providers.base import LLMProvider
from app.providers.schemas import LLMRequest, LLMResponse

logger = get_logger(__name__)

_DEFAULT_MODEL = "claude-haiku-4-5-20251001"


class AnthropicLLMProvider(LLMProvider):
    """Claude via the official anthropic SDK (async only)."""

    def _validate_config(self) -> None:
        if not self.api_key:
            raise ValueError("Anthropic API key is required (LLM_API_KEY)")
        self._client = AsyncAnthropic(api_key=self.api_key)
        self._default_model = self.config.get("model", _DEFAULT_MODEL)
        logger.info(f"AnthropicLLMProvider initialized: model={self._default_model}")

    async def generate(self, request: LLMRequest) -> LLMResponse:
        kwargs: Dict[str, Any] = {
            "model": request.model or self._default_model,
            "messages": [{"role": "user", "content": request.prompt}],
            "max_tokens": request.max_tokens or 4096,
            "temperature": request.temperature,
        }
        if request.system_prompt:
            kwargs["system"] = request.system_prompt

        try:
            raw = await self._client.messages.create(**kwargs)
        except APIStatusError as e:
            logger.error(f"Anthropic API error {e.status_code}: {e.message}")
            raise
        except APIConnectionError as e:
            logger.error(f"Anthropic connection error: {e}")
            raise

        return LLMResponse(
            content=raw.content[0].text,
            model=raw.model,
            provider=self.provider_name,
            tokens_used=raw.usage.input_tokens + raw.usage.output_tokens,
            metadata={"stop_reason": raw.stop_reason},
        )

    @property
    def provider_name(self) -> str:
        return "anthropic"
