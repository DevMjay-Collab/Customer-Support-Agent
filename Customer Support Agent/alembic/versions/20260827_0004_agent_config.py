"""agent configuration

Revision ID: 20260827_0004
Revises: 20260827_0003
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260827_0004"
down_revision: str | None = "20260827_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("system_instructions", sa.Text(), nullable=False, server_default=""),
        sa.Column("personality", sa.Text()),
        sa.Column("language", sa.String(32), nullable=False, server_default="en"),
        sa.Column("voice_provider", sa.String(64)),
        sa.Column("voice_id", sa.String(256)),
        sa.Column("allowed_tools_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("escalation_rules_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("lead_scoring_config_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("agent_configs")
