"""track completed learning sections

Revision ID: c31a6c7e9f02
Revises: 82af08f9e63d
Create Date: 2026-10-11
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c31a6c7e9f02"
down_revision: Union[str, Sequence[str], None] = "82af08f9e63d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "learning_progress",
        sa.Column("completed_section_ids", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("learning_progress", "completed_section_ids")
