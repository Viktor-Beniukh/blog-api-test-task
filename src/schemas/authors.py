from datetime import datetime

from typing import Annotated, Optional
from annotated_types import MinLen, MaxLen

from pydantic import BaseModel, EmailStr, ConfigDict, Field

from src.core.database.models.enums import Role
from src.schemas.profiles import ProfileResponse


class AuthorBase(BaseModel):
    username: Annotated[str, MinLen(3), MaxLen(32)]
    email: EmailStr


class AuthorCreate(AuthorBase):
    password: Annotated[str, MinLen(8), MaxLen(1024)]


class AuthorResponse(AuthorBase):
    model_config = ConfigDict(from_attributes=True)

    profile: Optional[ProfileResponse] = {}
    registered_at: datetime
    updated_at: datetime
    is_active: bool
    role: Role
    id: int


class AuthorChangeRole(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: Role


class AuthorMessageResponse(BaseModel):
    message: str


class TokenModel(BaseModel):
    access_token: str
    token_type: str
    author: AuthorResponse


class PasswordChangeModel(BaseModel):
    old_password: str = Field(min_length=8, max_length=255)
    new_password: str = Field(min_length=8, max_length=255)
    new_password_confirm: str = Field(min_length=8, max_length=255)


class AuthorResponseWithMessage(BaseModel):
    author: AuthorResponse
    message: str
