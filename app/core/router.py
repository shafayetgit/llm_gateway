import time
from fastapi import HTTPException, status
from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models.model_config import ModelConfig
from app.providers.base import BaseLLMProvider
from app.providers.google import GoogleProvider
from app.providers.ollama import OllamaProvider


class ModelRouter:
    def __init__(self, ttl_seconds: float = 60.0) -> None:
        self.providers: dict[str, BaseLLMProvider] = {
            "ollama": OllamaProvider(),
            "google": GoogleProvider(),
        }
        self.ttl = ttl_seconds
        # In-memory cache: model_name -> (provider_key, expiration_timestamp)
        self._cache: dict[str, tuple[str, float]] = {}

    async def get_provider(self, model_name: str) -> BaseLLMProvider:
        now = time.monotonic()

        # 1. Check in-memory cache for an unexpired entry
        if model_name in self._cache:
            provider_key, expires_at = self._cache[model_name]
            if now < expires_at:
                return self.providers[provider_key]
            del self._cache[model_name]

        # 2. Query PostgreSQL for active model configuration
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ModelConfig).where(
                    ModelConfig.name == model_name,
                    ModelConfig.is_active == True,
                )
            )
            config = result.scalar_one_or_none()

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model '{model_name}' is not found or inactive.",
            )

        provider = self.providers.get(config.provider)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Provider '{config.provider}' configured for model '{model_name}' is not supported.",
            )

        # 3. Cache the resolved provider
        self._cache[model_name] = (config.provider, now + self.ttl)
        return provider


model_router = ModelRouter()