from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database.db_settings.base import Base
from src.core.database.models.enums import Role

if TYPE_CHECKING:
    from src.core.database.models.profiles import Profile
    from src.core.database.models.posts import Post


class Author(Base):
    username: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    role: Mapped[Enum[Role]] = mapped_column(Enum(Role), default=Role.user)
    refresh_token: Mapped[str] = mapped_column(String(500), nullable=True)
    registered_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, server_default=func.now()
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    profile: Mapped["Profile"] = relationship(lazy="selectin", back_populates="author")
    posts: Mapped[list["Post"]] = relationship(lazy="selectin", back_populates="author")

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, username={self.username!r})"

    def __repr__(self):
        return str(self)
