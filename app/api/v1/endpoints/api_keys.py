import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import generate_api_key, get_db, verify_admin_secret
from app.models.api_key import ApiKey
from app.schemas.api_key import ApiKeyCreate, ApiKeyCreateResponse, ApiKeyResponse

router = APIRouter(dependencies=[Depends(verify_admin_secret)])


@router.post(
    "", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED
)
async def create_api_key(
    payload: ApiKeyCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Creates a new API key for a client app.
    raw_key, key_prefix, key_hash = generate_api_key()

    api_key_obj = ApiKey(
        name=payload.name,
        app_name=payload.app_name,
        key_hash=key_hash,
        key_prefix=key_prefix,
    )

    db.add(api_key_obj)
    await db.commit()
    await db.refresh(api_key_obj)

    return ApiKeyCreateResponse(
        id=api_key_obj.id,
        name=api_key_obj.name,
        app_name=api_key_obj.app_name,
        key_prefix=api_key_obj.key_prefix,
        is_active=api_key_obj.is_active,
        created_at=api_key_obj.created_at,
        raw_key=raw_key,
    )


@router.get("", response_model=list[ApiKeyResponse])
async def list_api_keys(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(ApiKey).order_by(ApiKey.created_at.desc()))
    return result.scalars().all()


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(ApiKey).where(ApiKey.id == key_id))
    api_key_obj = result.scalar_one_or_none()

    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API Key not found",
        )

    api_key_obj.is_active = False
    await db.commit()
