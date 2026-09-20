from collections.abc import AsyncGenerator
from typing import Any

import httpx
from fastapi import HTTPException, status

from app.core import settings

from .base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=180.0)
        return self._client

    async def chat_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any] | AsyncGenerator[str]:
        url = f"{self.base_url}/v1/chat/completions"

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if kwargs.get("tools"):
            payload["tools"] = kwargs["tools"]
        if kwargs.get("tool_choice"):
            payload["tool_choice"] = kwargs["tool_choice"]

        try:
            if stream:
                async def stream_generator() -> AsyncGenerator[str]:
                    async with self.client.stream("POST", url, json=payload) as response:
                        response.raise_for_status()
                        async for chunk in response.aiter_text():
                            yield chunk
                return stream_generator()

            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Ollama provider error: {exc.response.text}",
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Unable to reach Ollama server at {self.base_url}: {exc}",
            )

    async def create_embeddings(
        self,
        model: str,
        input_texts: list[str] | str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        url = f"{self.base_url}/v1/embeddings"

        payload: dict[str, Any] = {
            "model": model,
            "input": input_texts,
        }
        if kwargs.get("dimensions"):
            payload["dimensions"] = kwargs["dimensions"]
        if kwargs.get("encoding_format"):
            payload["encoding_format"] = kwargs["encoding_format"]

        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Ollama embedding error: {exc.response.text}",
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Unable to reach Ollama server at {self.base_url}: {exc}",
            )
