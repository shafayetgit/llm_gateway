from fastapi import APIRouter

from .endpoints import api_keys, chat, embeddings, models

router = APIRouter()
router.include_router(api_keys.router, prefix="/api-keys", tags=["API Keys"])
router.include_router(chat.router, tags=["Chat"])
router.include_router(embeddings.router, tags=["Embeddings"])
router.include_router(models.router, tags=["Models"])
