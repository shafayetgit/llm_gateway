from collections.abc import AsyncGenerator
from typing import Any
import httpx
from fastapi import HTTPException, status
from app.core import settings
from .base import BaseLLMProvider


class GoogleProvider(BaseLLMProvider):
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or settings.google_api_key
        self.base_url = (base_url or settings.google_base_url).rstrip("/")
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                headers["X-goog-api-key"] = self.api_key
            self._client = httpx.AsyncClient(headers=headers, timeout=120.0)
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
        if not self.api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google API key is not configured.",
            )

        # Ensure role="tool" messages always have `name` for Google's OpenAI-compat layer
        tool_id_to_name: dict[str, str] = {}
        for msg in messages:
            if msg.get("role") == "assistant" and msg.get("tool_calls"):
                for tc in msg["tool_calls"]:
                    tc_id = tc.get("id")
                    fn_name = tc.get("function", {}).get("name")
                    if tc_id and fn_name:
                        tool_id_to_name[tc_id] = fn_name
            elif msg.get("role") == "tool":
                tc_id = msg.get("tool_call_id")
                if not msg.get("name") and tc_id and tc_id in tool_id_to_name:
                    msg["name"] = tool_id_to_name[tc_id]
                if msg.get("content") is None:
                    msg["content"] = ""

        url = f"{self.base_url}/chat/completions"
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
            raise HTTPException(status_code=exc.response.status_code, detail=f"Google error: {exc.response.text}")
        except httpx.RequestError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Google API unreachable: {exc}")

    async def create_embeddings(
        self,
        model: str,
        input_texts: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        if not self.api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google API key is not configured.",
            )

        items = input_texts if isinstance(input_texts, list) else [input_texts]
        if any(hasattr(item, "model_dump") or isinstance(item, dict) for item in items):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model '{model}' via Google OpenAI-compatible endpoint does not support structured multimodal embedding inputs.",
            )

        url = f"{self.base_url}/embeddings"
        payload = {"model": model, "input": input_texts}
        if kwargs.get("dimensions"):
            payload["dimensions"] = kwargs["dimensions"]

        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=f"Google embedding error: {exc.response.text}")
        except httpx.RequestError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Google API unreachable: {exc}")