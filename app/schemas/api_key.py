import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApiKeyCreate(BaseModel):
    name: str
    app_name: str


class ApiKeyResponse(BaseModel):
    id: uuid.UUID
    name: str
    app_name: str
    key_prefix: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApiKeyCreateResponse(ApiKeyResponse):
    raw_key: str
