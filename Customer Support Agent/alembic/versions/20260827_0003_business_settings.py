"""single-workspace business settings

Revision ID: 20260827_0003
Revises: 20260827_0002
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260827_0003"
down_revision: str | None = "20260827_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "business_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("business_name", sa.String(200), nullable=False),
        sa.Column("business_description", sa.String(4000)),
        sa.Column("website", sa.String(2048)),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="UTC"),
        sa.Column("business_hours_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("support_email", sa.String(320)),
        sa.Column("support_phone", sa.String(32)),
        sa.Column("default_calendar_id", sa.String(512)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("business_settings")
