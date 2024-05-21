from datetime import datetime

from sqlalchemy import String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database.db_settings.base import Base
from src.core.database.models.mixins import AuthorRelationMixin


class Profile(AuthorRelationMixin, Base):
    _author_id_unique = True
    _author_back_populates = "profile"

    first_name: Mapped[str] = mapped_column(String(40), nullable=True)
    last_name: Mapped[str] = mapped_column(String(40), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(50), nullable=True)
    image: Mapped[str] = mapped_column(String(255), nullable=True)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    facebook: Mapped[str] = mapped_column(String(255), nullable=True)
    twitter: Mapped[str] = mapped_column(String(255), nullable=True)
    instagram: Mapped[str] = mapped_column(String(255), nullable=True)
    telegram: Mapped[str] = mapped_column(String(255), nullable=True)
    youtube: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, server_default=func.now()
    )

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return str(self)
