from app.providers.base import BaseLLMProvider
from app.providers.google import GoogleProvider
from app.providers.ollama import OllamaProvider


class ModelRouter:
    def __init__(self) -> None:
        # Registry of instantiated backend providers
        self.providers: dict[str, BaseLLMProvider] = {
            "ollama": OllamaProvider(),
            "google": GoogleProvider(),
        }

    def get_provider(self, model_name: str) -> BaseLLMProvider:
        # Route Gemini and Google embedding models to Google
        if model_name.startswith(("gemini", "text-embedding-")):
            provider_key = "google"
        else:
            provider_key = "ollama"

        provider = self.providers.get(provider_key)
        if not provider:
            raise ValueError(
                f"Provider '{provider_key}' not configured for model '{model_name}'"
            )

        return provider


model_router = ModelRouter()
