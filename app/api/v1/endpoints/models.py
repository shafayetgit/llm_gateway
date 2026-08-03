from typing import Annotated

from fastapi import APIRouter, Depends

from app.core import verify_api_key
from app.models.api_key import ApiKey

router = APIRouter()


@router.get("/models")
async def list_models(
    api_key: Annotated[ApiKey, Depends(verify_api_key)],
):
    """OpenAI-compatible list models endpoint."""
    return {
        "object": "list",
        "data": [
            {
                "id": "gemma4",
                "object": "model",
                "created": 1700000000,
                "owned_by": "ollama",
            },
            {
                "id": "llama3",
                "object": "model",
                "created": 1700000000,
                "owned_by": "ollama",
            },
        ],
    }
