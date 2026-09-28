"""core contacts, leads, conversations, and messages

Revision ID: 20260827_0005
Revises: 20260827_0004
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260827_0005"
down_revision: str | None = "20260827_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("contacts", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("name", sa.String(200)), sa.Column("phone", sa.String(32)), sa.Column("email", sa.String(320)), sa.Column("company", sa.String(200)), sa.Column("metadata_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")))
    op.create_index("ix_contacts_phone", "contacts", ["phone"])
    op.create_index("ix_contacts_email", "contacts", ["email"])
    op.create_table("leads", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("contact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contacts.id"), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("qualification_status", sa.String(32)), sa.Column("score", sa.Integer(), nullable=False, server_default="0"), sa.Column("intent", sa.String(128)), sa.Column("source", sa.String(128)), sa.Column("campaign", sa.String(256)), sa.Column("utm_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")))
    op.create_index("ix_leads_status", "leads", ["status"])
    op.create_index("ix_leads_score", "leads", ["score"])
    op.create_table("conversations", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("contact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contacts.id"), nullable=False), sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("leads.id")), sa.Column("channel", sa.String(32), nullable=False), sa.Column("status", sa.String(32), nullable=False), sa.Column("current_state", sa.String(64), nullable=False), sa.Column("intent", sa.String(128)), sa.Column("secondary_intent", sa.String(128)), sa.Column("summary", sa.Text()), sa.Column("next_action", sa.String(256)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")))
    op.create_index("ix_conversations_status", "conversations", ["status"])
    op.create_index("ix_conversations_updated_at", "conversations", ["updated_at"])
    op.create_table("messages", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id"), nullable=False), sa.Column("provider_message_id", sa.String(256)), sa.Column("role", sa.String(32), nullable=False), sa.Column("content", sa.Text(), nullable=False), sa.Column("message_type", sa.String(32), nullable=False), sa.Column("metadata_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'")), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")))
    op.create_index("ix_messages_conversation_created", "messages", ["conversation_id", "created_at"])


def downgrade() -> None:
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("leads")
    op.drop_table("contacts")
