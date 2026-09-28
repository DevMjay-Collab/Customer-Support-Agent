from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class AgentConfig(Base):
    __tablename__ = "agent_configs"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(32), default="active")
    system_instructions: Mapped[str] = mapped_column(Text, default="")
    personality: Mapped[str | None] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(32), default="en")
    voice_provider: Mapped[str | None] = mapped_column(String(64))
    voice_id: Mapped[str | None] = mapped_column(String(256))
    allowed_tools_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    escalation_rules_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    lead_scoring_config_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
