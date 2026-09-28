"""foundation baseline

Revision ID: 20260826_0001
Revises:
Create Date: 2026-08-26 00:00:00
"""

from alembic import op

revision: str = "20260826_0001"
down_revision: str | None = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Establish Alembic versioning before Phase 3 domain tables."""
    op.execute("SELECT 1")


def downgrade() -> None:
    op.execute("SELECT 1")

