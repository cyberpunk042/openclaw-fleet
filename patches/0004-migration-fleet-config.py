"""add fleet_config JSON column to boards

Revision ID: g1a2b3c4d5e6
Revises: a9b1c2d3e4f7
Create Date: 2026-03-30 00:00:00.000000

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "g1a2b3c4d5e6"
down_revision = "a9b1c2d3e4f7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    board_columns = {column["name"] for column in inspector.get_columns("boards")}
    if "fleet_config" not in board_columns:
        op.add_column(
            "boards",
            sa.Column(
                "fleet_config",
                sa.JSON(),
                nullable=True,
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    board_columns = {column["name"] for column in inspector.get_columns("boards")}
    if "fleet_config" in board_columns:
        op.drop_column("boards", "fleet_config")