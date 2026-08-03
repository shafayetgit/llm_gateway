from fastapi import FastAPI

from app.bootstrap import setup_docs, setup_middlewares, setup_routes
from app.core import settings
from app.core.exceptions import setup_exception_handlers

app = FastAPI(
    title=settings.app_name,
    description="API Gateway for managing local & cloud LLMs",
    version="0.1.0",
    debug=settings.debug,
)

setup_docs(app)
setup_middlewares(app)
setup_routes(app)
setup_exception_handlers(app)
