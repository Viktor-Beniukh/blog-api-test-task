from typing import Annotated
from annotated_types import MinLen, MaxLen

from pydantic import BaseModel, ConfigDict


class TagBase(BaseModel):
    name: Annotated[str, MinLen(3), MaxLen(30)]


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    pass


class TagResponse(TagBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
