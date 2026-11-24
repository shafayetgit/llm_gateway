import asyncio
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.core.db import AsyncSessionLocal
from app.models.model_config import ModelConfig

DEFAULT_MODELS = [
    # Ollama Models
    {"name": "bge-m3:567m", "provider": "ollama"},
    {"name": "gemma4:31b-cloud", "provider": "ollama"},
    {"name": "gemma4:e2b", "provider": "ollama"},
    {"name": "gemma4:e2b-it-qat", "provider": "ollama"},
    {"name": "lfm3-vl:latest", "provider": "ollama"},
    {"name": "llama3", "provider": "ollama"},
    # Google Gemini Models
    {"name": "gemini-3.8-flash", "provider": "google"},
    {"name": "gemini-4-hydrogen", "provider": "google"},
    {"name": "text-embedding-004", "provider": "google"},
    # Local Multimodal Embedding Models
    {"name": "google/embeddinggemma-2", "provider": "sentence_transformer"},
]


async def seed_models() -> None:
    print("🌱 Seeding model configurations...")

    async with AsyncSessionLocal() as session:
        for model_data in DEFAULT_MODELS:
            stmt = (
                insert(ModelConfig)
                .values(
                    name=model_data["name"],
                    provider=model_data["provider"],
                    is_active=True,
                )
                .on_conflict_do_update(
                    index_elements=["name"],
                    set_={
                        "name": model_data["name"],
                        "provider": model_data["provider"],
                        "is_active": True,
                    },
                )
            )
            await session.execute(stmt)

        await session.commit()

        # Query and display current active models
        result = await session.execute(
            select(ModelConfig.name, ModelConfig.provider).where(
                ModelConfig.is_active == True
            )
        )
        active_models = result.all()

    print("\n✅ Successfully synced models in database:")
    for name, provider in active_models:
        print(f"  • {name:<22} -> provider: {provider}")


if __name__ == "__main__":
    asyncio.run(seed_models())
    
    
# Command to run the script:
# uv run python -m scripts.seed_models