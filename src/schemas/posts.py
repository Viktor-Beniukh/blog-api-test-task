from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PostBase(BaseModel):
    title: str
    content: str


class PostCreate(PostBase):
    pass


class PostPartialUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class PostMessageResponse(BaseModel):
    message: str


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    author_id: int
    category_id: int
    image: Optional[str]
    created_at: datetime
    updated_at: datetime
    id: int
