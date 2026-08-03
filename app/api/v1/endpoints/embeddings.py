from typing import Annotated

from fastapi import APIRouter, Depends

from app.core import model_router, verify_api_key
from app.models.api_key import ApiKey
from app.schemas.openai import EmbeddingRequest

router = APIRouter()


@router.post("/embeddings")
async def create_embeddings(
    payload: EmbeddingRequest,
    api_key: Annotated[ApiKey, Depends(verify_api_key)],
):
    # 1. Resolve provider for requested model
    provider = model_router.get_provider(payload.model)

    # 2. Forward request to provider
    response = await provider.create_embeddings(
        model=payload.model,
        input_texts=payload.input,
    )

    return response
