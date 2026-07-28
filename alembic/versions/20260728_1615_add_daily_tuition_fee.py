"""Add per-class daily tuition fee."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260728_1615"
down_revision = "a825713c224b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "classes",
        sa.Column("daily_tuition_fee", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("classes", "daily_tuition_fee")
