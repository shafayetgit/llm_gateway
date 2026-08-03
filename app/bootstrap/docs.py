from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html


def setup_docs(app: FastAPI) -> None:

    @app.get("/docs", include_in_schema=False)
    async def custom_docs():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} Docs",
            swagger_favicon_url="/static/favicon.ico",
            swagger_ui_parameters={"defaultModelsExpandDepth": -1},
        )
