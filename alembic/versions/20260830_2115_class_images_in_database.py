"""Store class images on the classes row.

Revision ID: 20260830_2115
Revises: 20260825_0908
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260830_2115"
down_revision = "20260825_0908"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add deferred image columns persisted with the rest of the database."""
    op.add_column("classes", sa.Column("icon_mime", sa.String(length=64), nullable=True))
    op.add_column("classes", sa.Column("icon_data", sa.LargeBinary(), nullable=True))


def downgrade() -> None:
    """Remove class image columns."""
    op.drop_column("classes", "icon_data")
    op.drop_column("classes", "icon_mime")
