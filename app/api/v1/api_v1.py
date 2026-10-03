from fastapi import APIRouter

from .endpoints import api_keys, chat, embeddings, models

router = APIRouter()
router.include_router(api_keys.router, prefix="/api-keys", tags=["API Keys (Admin)"])
router.include_router(chat.router, tags=["Chat (Gateway User Endpoints)"])
router.include_router(embeddings.router, tags=["Embeddings (Gateway User Endpoints)"])
router.include_router(models.router, tags=["Models (Gateway User Endpoints)"])
