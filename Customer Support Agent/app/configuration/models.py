from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class BusinessSettings(Base):
    __tablename__ = "business_settings"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    business_name: Mapped[str] = mapped_column(String(200))
    business_description: Mapped[str | None] = mapped_column(String(4000))
    website: Mapped[str | None] = mapped_column(String(2048))
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")
    business_hours_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    support_email: Mapped[str | None] = mapped_column(String(320))
    support_phone: Mapped[str | None] = mapped_column(String(32))
    default_calendar_id: Mapped[str | None] = mapped_column(String(512))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
