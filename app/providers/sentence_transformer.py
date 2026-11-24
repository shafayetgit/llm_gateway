import asyncio
import base64
import io
import threading
from collections.abc import AsyncGenerator
from typing import Any

import httpx
import torch
from fastapi import HTTPException, status
from PIL import Image
from sentence_transformers import SentenceTransformer

from .base import BaseLLMProvider


class SentenceTransformerProvider(BaseLLMProvider):
    """Local multimodal embedding provider powered by SentenceTransformers."""

    def __init__(self) -> None:
        self._models: dict[str, SentenceTransformer] = {}
        self._load_lock = threading.Lock()

    def _get_model(self, model_name: str) -> SentenceTransformer:
        if model_name not in self._models:
            with self._load_lock:
                if model_name not in self._models:
                    dtype = (
                        torch.bfloat16
                        if torch.cuda.is_available() and torch.cuda.is_bf16_supported()
                        else torch.float32
                    )
                    self._models[model_name] = SentenceTransformer(
                        model_name,
                        model_kwargs={"torch_dtype": dtype},
                        # Load text + vision only (440M); remove audio_config=None when adding audio
                        config_kwargs={"audio_config": None},
                    )
        return self._models[model_name]

    async def _decode_image(self, source: str) -> Image.Image:
        """Decodes a base64 data URI or fetches an HTTP(S) image URL into a PIL Image."""
        try:
            if source.startswith(("http://", "https://")):
                async with httpx.AsyncClient(
                    timeout=30.0,
                    follow_redirects=True,
                    headers={"User-Agent": "llm-gateway/1.0"},
                ) as client:
                    resp = await client.get(source)
                    resp.raise_for_status()
                    return Image.open(io.BytesIO(resp.content)).convert("RGB")

            # Handle data URI (e.g. "data:image/jpeg;base64,...") or raw base64
            b64_data = source.split(",", 1)[1] if "," in source else source
            image_bytes = base64.b64decode(b64_data)
            return Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image input: {exc}",
            )

    async def _prepare_input(self, item: Any) -> Any:
        """Normalizes a single text or multimodal dict item for SentenceTransformer.encode()."""
        if not isinstance(item, dict):
            return item

        prepared: dict[str, Any] = {}
        if item.get("text") is not None:
            prepared["text"] = item["text"]

        if item.get("image") is not None:
            images = item["image"] if isinstance(item["image"], list) else [item["image"]]
            decoded = [await self._decode_image(img) for img in images]
            prepared["image"] = decoded if isinstance(item["image"], list) else decoded[0]

        # Future modalities (video, audio) can be decoded here
        return prepared

    async def chat_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: int | None = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any] | AsyncGenerator[str]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model '{model}' is an embedding-only model and does not support chat completions.",
        )

    async def create_embeddings(
        self,
        model: str,
        input_texts: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        # Normalize single item vs list of items
        is_batch = isinstance(input_texts, list)
        items = input_texts if is_batch else [input_texts]

        # Convert any Pydantic models to dicts and decode media
        raw_items = [
            item.model_dump(exclude_none=True) if hasattr(item, "model_dump") else item
            for item in items
        ]
        prepared_items = [await self._prepare_input(item) for item in raw_items]

        encode_kwargs: dict[str, Any] = {"normalize_embeddings": True}
        if kwargs.get("dimensions"):
            encode_kwargs["truncate_dim"] = kwargs["dimensions"]
        if kwargs.get("prompt_name"):
            encode_kwargs["prompt_name"] = kwargs["prompt_name"]

        def _encode() -> list[list[float]]:
            st_model = self._get_model(model)
            embeddings = st_model.encode(prepared_items, **encode_kwargs)
            return embeddings.tolist()

        vectors = await asyncio.to_thread(_encode)

        return {
            "object": "list",
            "data": [
                {
                    "object": "embedding",
                    "index": idx,
                    "embedding": vec,
                }
                for idx, vec in enumerate(vectors)
            ],
            "model": model,
            "usage": {"prompt_tokens": 0, "total_tokens": 0},
        }