from openai import AsyncOpenAI, APIStatusError, APIConnectionError

from app.core import get_logger
from app.providers.base import LLMProvider
from app.providers.schemas import LLMRequest, LLMResponse

logger = get_logger(__name__)

_GROK_BASE_URL = "https://api.x.ai/v1"
_DEFAULT_MODEL = "grok-3-mini"


class GrokLLMProvider(LLMProvider):
    """
    xAI Grok via OpenAI-compatible API.
    Uses the openai SDK pointed at https://api.x.ai/v1 with the Grok API key.
    """

    def _validate_config(self) -> None:
        if not self.api_key:
            raise ValueError("Grok API key is required (LLM_API_KEY)")
        self._client = AsyncOpenAI(api_key=self.api_key, base_url=_GROK_BASE_URL)
        self._default_model = self.config.get("model", _DEFAULT_MODEL)
        logger.info(f"GrokLLMProvider initialized: model={self._default_model}")

    async def generate(self, request: LLMRequest) -> LLMResponse:
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        try:
            raw = await self._client.chat.completions.create(
                model=request.model or self._default_model,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
        except APIStatusError as e:
            logger.error(f"Grok API error {e.status_code}: {e.message}")
            raise
        except APIConnectionError as e:
            logger.error(f"Grok connection error: {e}")
            raise

        return LLMResponse(
            content=raw.choices[0].message.content,
            model=raw.model,
            provider=self.provider_name,
            tokens_used=raw.usage.total_tokens if raw.usage else None,
            metadata={"finish_reason": raw.choices[0].finish_reason},
        )

    @property
    def provider_name(self) -> str:
        return "grok"
