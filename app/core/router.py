from app.providers.base import BaseLLMProvider
from app.providers.ollama import OllamaProvider


class ModelRouter:
    def __init__(self) -> None:
        # Registry of instantiated backend providers
        self.providers: dict[str, BaseLLMProvider] = {
            "ollama": OllamaProvider(),
        }

    def get_provider(self, model_name: str) -> BaseLLMProvider:
        provider_key = "ollama"

        provider = self.providers.get(provider_key)
        if not provider:
            raise ValueError(
                f"Provider '{provider_key}' not configured for model '{model_name}'"
            )

        return provider


model_router = ModelRouter()
