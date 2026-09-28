from pydantic import BaseModel, Field


class BusinessSettingsResponse(BaseModel):
    business_name: str
    business_description: str | None
    website: str | None
    timezone: str
    business_hours_json: dict[str, object]
    support_email: str | None
    support_phone: str | None
    default_calendar_id: str | None


class BusinessSettingsUpdate(BaseModel):
    business_name: str | None = Field(default=None, min_length=1, max_length=200)
    business_description: str | None = Field(default=None, max_length=4000)
    website: str | None = Field(default=None, max_length=2048)
    timezone: str | None = Field(default=None, min_length=1, max_length=64)
    business_hours_json: dict[str, object] | None = None
    support_email: str | None = Field(default=None, max_length=320)
    support_phone: str | None = Field(default=None, max_length=32)
    default_calendar_id: str | None = Field(default=None, max_length=512)
