from sqlalchemy import Table, Column, Integer, ForeignKey, UniqueConstraint

from src.core.database.db_settings.base import Base

post_tag_association_table = Table(
    "post_tag_association",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("post_id", ForeignKey("posts.id")),
    Column("tag_id", ForeignKey("tags.id")),
    UniqueConstraint("post_id", "tag_id", name="idx_unique_post_tag"),
)
