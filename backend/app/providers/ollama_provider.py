import asyncio

import httpx

from app.core import get_logger
from app.providers.base import LLMProvider
from app.providers.schemas import LLMRequest, LLMResponse

logger = get_logger(__name__)

_DEFAULT_HOST = "http://localhost:11434"
_DEFAULT_MODEL = "llama3.2"
_REQUEST_TIMEOUT = 120.0  # local model inference can be slow


class OllamaLLMProvider(LLMProvider):
    """
    Local Ollama provider.
    Talks to a locally-running Ollama server via its REST API.
    No API key is required; set OLLAMA_HOST to override the default address.
    """

    def _validate_config(self) -> None:
        self._host = self.config.get("host", _DEFAULT_HOST).rstrip("/")
        logger.info(f"OllamaLLMProvider initialized: host={self._host}, model={self._model}")

    @property
    def _model(self) -> str:
        return self.config.get("model", _DEFAULT_MODEL)

    def _build_payload(self, request: LLMRequest) -> dict:
        messages = []
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})
        messages.append({"role": "user", "content": request.prompt})

        payload: dict = {
            "model": request.model or self._model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": request.temperature},
        }
        if request.max_tokens:
            payload["options"]["num_predict"] = request.max_tokens
        return payload

    def _to_response(self, data: dict, model: str) -> LLMResponse:
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

    async def generate(self, request: LLMRequest) -> LLMResponse:
        payload = self._build_payload(request)
        try:
            async with httpx.AsyncClient(timeout=_REQUEST_TIMEOUT) as client:
                resp = await client.post(f"{self._host}/api/chat", json=payload)
                resp.raise_for_status()
            return self._to_response(resp.json(), payload["model"])
        except httpx.ConnectError:
            logger.error(f"Cannot connect to Ollama at {self._host} — is it running?")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama API error {e.response.status_code}: {e.response.text}")
            raise

    def generate_sync(self, request: LLMRequest) -> LLMResponse:
        payload = self._build_payload(request)
        try:
            with httpx.Client(timeout=_REQUEST_TIMEOUT) as client:
                resp = client.post(f"{self._host}/api/chat", json=payload)
                resp.raise_for_status()
            return self._to_response(resp.json(), payload["model"])
        except httpx.ConnectError:
            logger.error(f"Cannot connect to Ollama at {self._host} — is it running?")
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama API error {e.response.status_code}: {e.response.text}")
            raise

    async def batch_generate(self, requests: list[LLMRequest]) -> list[LLMResponse]:
        # Ollama is single-threaded by default; gather still helps pipeline async I/O
        return list(await asyncio.gather(*[self.generate(r) for r in requests]))

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def available_models(self) -> list[str]:
        # Installed models vary per machine; return the configured default
        return [self._model]
