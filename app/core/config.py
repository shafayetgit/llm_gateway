from functools import lru_cache

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LLM API Gateway"
    app_env: str
    debug: bool = False

    # Database
    database_url: str

    # Security
    secret_key: str

    # Ollama Provider
    ollama_base_url: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @computed_field
    @property
    def test_database_url(self) -> str:
        if "/llm_gateway" in self.database_url:
            return self.database_url.replace("/llm_gateway", "/llm_gateway_test")
        return f"{self.database_url}_test"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
