import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1 import api_v1
from app.core import settings


def setup_routes(app: FastAPI):
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")

    app.include_router(api_v1.router, prefix="/api/v1")

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "online",
            "app_name": settings.app_name,
            "environment": settings.app_env,
        }
