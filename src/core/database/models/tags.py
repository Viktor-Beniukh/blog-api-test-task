from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.db_settings.base import Base
from src.core.database.models.post_tag_association import post_tag_association_table

if TYPE_CHECKING:
    from src.core.database.models.posts import Post


class Tag(Base):
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)

    posts: Mapped["Post"] = relationship(
        secondary=post_tag_association_table, lazy="selectin", back_populates="tags"
    )

    @staticmethod
    def add_hashtag(name: str) -> str:
        if not name.startswith("#"):
            return f"#{name.lower()}"
        return name.lower()

    def __repr__(self):
        return f"<Tag(name={self.name})>"
