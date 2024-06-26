"""create profiles table

Revision ID: 06ea94b021b9
Revises: 966151e38bca
Create Date: 2024-05-21 11:33:44.422789

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "06ea94b021b9"
down_revision: Union[str, None] = "966151e38bca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("first_name", sa.String(length=40), nullable=True),
        sa.Column("last_name", sa.String(length=40), nullable=True),
        sa.Column("phone_number", sa.String(length=50), nullable=True),
        sa.Column("image", sa.String(length=255), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("facebook", sa.String(length=255), nullable=True),
        sa.Column("twitter", sa.String(length=255), nullable=True),
        sa.Column("instagram", sa.String(length=255), nullable=True),
        sa.Column("telegram", sa.String(length=255), nullable=True),
        sa.Column("youtube", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["authors.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("author_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("profiles")
    # ### end Alembic commands ###
