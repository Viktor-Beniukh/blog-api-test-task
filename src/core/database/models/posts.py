from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.db_settings.base import Base
from src.core.database.models.mixins import AuthorRelationMixin
from src.core.database.models.utils import slugify

if TYPE_CHECKING:
    from src.core.database.models.categories import Category


class Post(AuthorRelationMixin, Base):
    _author_back_populates = "posts"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)
    content: Mapped[str] = mapped_column(String(500), default="", server_default="")
    image: Mapped[str] = mapped_column(String(255), nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, server_default=func.now()
    )

    category: Mapped["Category"] = relationship(lazy="selectin", back_populates="posts")

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self) -> None:
        if self.title:
            self.slug = slugify(self.title).lower()

    def __repr__(self):
        return f"{self.id}: {self.title}"
