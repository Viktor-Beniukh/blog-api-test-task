from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    name: str


class CategoryChange(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    id: int
