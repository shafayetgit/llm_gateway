from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, verify_api_key
from app.models.api_key import ApiKey
from app.models.model_config import ModelConfig

router = APIRouter()


@router.get("/models")
async def list_models(
    api_key: Annotated[ApiKey, Depends(verify_api_key)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """OpenAI-compatible list models endpoint querying active models from database."""
    result = await db.execute(
        select(ModelConfig)
        .where(ModelConfig.is_active == True)
        .order_by(ModelConfig.created_at)
    )
    models = result.scalars().all()

    return {
        "object": "list",
        "data": [
            {
                "id": model.name,
                "object": "model",
                "created": int(model.created_at.timestamp()),
                "owned_by": model.provider,
            }
            for model in models
        ],
    }