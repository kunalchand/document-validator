import httpx

from app.core import get_logger
from app.providers.base import LLMProvider
from app.providers.schemas import LLMRequest, LLMResponse

logger = get_logger(__name__)

_DEFAULT_HOST = "http://localhost:11434"
_DEFAULT_MODEL = "llama2"
_REQUEST_TIMEOUT = 180.0  # local inference can be slow on CPU-bound boxes


class OllamaLLMProvider(LLMProvider):
    """
    Local Ollama provider — talks to a locally-running Ollama server via its REST API.
    No API key required. Override the address by setting OLLAMA_HOST in the environment.
    """

    def _validate_config(self) -> None:
        self._host = self.config.get("host", _DEFAULT_HOST).rstrip("/")
        self._default_model = self.config.get("model", _DEFAULT_MODEL)
        logger.info(f"OllamaLLMProvider initialized: host={self._host}, model={self._default_model}")

    async def generate(self, request: LLMRequest) -> LLMResponse:
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        model = request.model or self._default_model
        payload: dict = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": request.temperature},
        }
        if request.max_tokens:
            payload["options"]["num_predict"] = request.max_tokens

        try:
            async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT) as client:
                resp = await client.post(f"{self._host}/api/chat", json=payload)
                resp.raise_for_status()
        except httpx.ConnectError:
            logger.error(f"Cannot connect to Ollama at {self._host} — is it running?")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama API error {e.response.status_code}: {e.response.text}")
            raise

        data = resp.json()
        return LLMResponse(
            content=data["message"]["content"],
            model=model,
            provider=self.provider_name,
            tokens_used=data.get("eval_count"),
            metadata={
                "prompt_eval_count": data.get("prompt_eval_count"),
                "total_duration_ns": data.get("total_duration"),
            },
        )

    @property
    def provider_name(self) -> str:
        return "ollama"
