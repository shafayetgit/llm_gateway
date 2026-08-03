from app.core.exceptions import setup_exception_handlers

from .docs import setup_docs
from .middlewares import setup_middlewares
from .routes import setup_routes

__all__ = [
    "setup_docs",
    "setup_exception_handlers",
    "setup_middlewares",
    "setup_routes",
]
