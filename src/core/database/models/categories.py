from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.db_settings.base import Base
from src.core.database.models.utils import slugify

if TYPE_CHECKING:
    from src.core.database.models.posts import Post


class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)

    posts: Mapped[list["Post"]] = relationship(lazy="selectin", back_populates="category")

    def __init__(self, *args, **kwargs):
        super(Category, self).__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self) -> None:
        if self.name:
            self.slug = slugify(self.name).lower()

    def __repr__(self):
        return self.name
