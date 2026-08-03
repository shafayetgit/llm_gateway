from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import settings


def setup_middlewares(app: FastAPI) -> None:
    pass
