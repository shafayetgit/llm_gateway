from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any


class BaseLLMProvider(ABC):
    @abstractmethod
    async def chat_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any] | AsyncGenerator[str]:
        pass

    @abstractmethod
    async def create_embeddings(
        self,
        model: str,
        input_texts: list[str] | str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        pass
