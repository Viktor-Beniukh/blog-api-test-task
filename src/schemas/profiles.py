from datetime import datetime

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProfileBase(BaseModel):
    first_name: Optional[str] = ""
    last_name: Optional[str] = ""


class ProfileCreate(ProfileBase):
    pass


class ProfilePartialUpdate(ProfileBase):
    phone_number: Optional[str] = Field(max_length=16, default="")
    bio: Optional[str] = ""
    facebook: Optional[str] = ""
    twitter: Optional[str] = ""
    instagram: Optional[str] = ""
    telegram: Optional[str] = ""
    youtube: Optional[str] = ""


class ProfileResponse(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    phone_number: Optional[str] = ""
    image: Optional[str] = ""
    bio: Optional[str] = ""
    facebook: Optional[str] = ""
    twitter: Optional[str] = ""
    instagram: Optional[str] = ""
    telegram: Optional[str] = ""
    youtube: Optional[str] = ""
    created_at: datetime
    updated_at: datetime
    author_id: int
    id: int
