from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core import model_router, verify_api_key
from app.models.api_key import ApiKey
from app.schemas.openai import ChatCompletionRequest

router = APIRouter()


@router.post("/chat/completions")
async def create_chat_completion(
    payload: ChatCompletionRequest,
    api_key: Annotated[ApiKey, Depends(verify_api_key)],
):

    # 1. Resolve provider for requested model
    provider = model_router.get_provider(payload.model)

    # 2. Forward request to provider
    response = await provider.chat_completion(
        model=payload.model,
        messages=[msg.model_dump(exclude_none=True) for msg in payload.messages],
        temperature=payload.temperature or 0.7,
        max_tokens=payload.max_tokens,
        stream=payload.stream,
        tools=payload.tools,
        tool_choice=payload.tool_choice,
    )

    if isinstance(response, AsyncGenerator):
        return StreamingResponse(response, media_type="text/event-stream")

    return response
