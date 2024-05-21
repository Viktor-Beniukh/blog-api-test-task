from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.db_settings.base import Base
from src.core.database.models.post_tag_association import post_tag_association_table
from src.core.database.models.utils import format_tag_name

if TYPE_CHECKING:
    from src.core.database.models.posts import Post


class Tag(Base):
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)

    posts: Mapped[list["Post"]] = relationship(
        secondary=post_tag_association_table, back_populates="tags"
    )

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)
        self.add_hashtag()

    def add_hashtag(self):
        if self.name:
            self.name = format_tag_name(self.name)

    def __repr__(self):
        return f"<Tag(name={self.name})>"
