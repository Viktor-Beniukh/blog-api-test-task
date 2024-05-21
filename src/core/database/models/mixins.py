from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import declared_attr, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from src.core.database.models import Author


class AuthorRelationMixin:
    _author_id_nullable: bool = False
    _author_id_unique: bool = False
    _author_back_populates: str | None = None

    @declared_attr
    def author_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey("authors.id"),
            unique=cls._author_id_unique,
            nullable=cls._author_id_nullable,
        )

    @declared_attr
    def author(cls) -> Mapped["Author"]:
        return relationship(
            "Author",
            back_populates=cls._author_back_populates,
            lazy="subquery"
        )
