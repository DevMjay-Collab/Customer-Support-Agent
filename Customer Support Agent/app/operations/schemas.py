from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

ContactMethod = Literal["email", "phone", "web", "whatsapp", "sms", "voice", "import"]
LeadStatus = Literal["new", "qualified", "disqualified", "nurturing"]
ConversationChannel = Literal["email", "web", "whatsapp", "sms", "voice", "internal"]
ConversationStatus = Literal["active", "waiting", "resolved", "closed"]
MessageRole = Literal["customer", "agent", "assistant", "system"]


class ContactFields(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=32)
    email: str | None = Field(default=None, max_length=320)
    company: str | None = Field(default=None, max_length=200)
    metadata_json: dict[str, object] = Field(default_factory=dict)


class ContactCreate(ContactFields):
    @model_validator(mode="after")
    def includes_contact_information(self) -> "ContactCreate":
        if not any((self.name, self.phone, self.email, self.company)):
            raise ValueError("Provide at least one identifying contact field.")
        return self


class ContactUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=32)
    email: str | None = Field(default=None, max_length=320)
    company: str | None = Field(default=None, max_length=200)
    metadata_json: dict[str, object] | None = None

    @model_validator(mode="after")
    def includes_change(self) -> "ContactUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update.")
        return self


class ContactResponse(ContactFields):
    id: UUID
    created_at: datetime
    updated_at: datetime


class ContactPage(BaseModel):
    items: list[ContactResponse]
    limit: int
    offset: int


class LeadCreate(BaseModel):
    status: LeadStatus = "new"
    qualification_status: str | None = Field(default=None, max_length=32)
    score: int = Field(default=0, ge=0, le=100)
    intent: str | None = Field(default=None, max_length=128)
    source: ContactMethod | None = None
    campaign: str | None = Field(default=None, max_length=256)
    utm_json: dict[str, object] = Field(default_factory=dict)


class LeadResponse(LeadCreate):
    id: UUID
    contact_id: UUID
    created_at: datetime
    updated_at: datetime


class LeadPage(BaseModel):
    items: list[LeadResponse]
    limit: int
    offset: int


class ConversationCreate(BaseModel):
    contact_id: UUID
    lead_id: UUID | None = None
    channel: ConversationChannel
    current_state: str = Field(default="NEW", min_length=1, max_length=64)
    intent: str | None = Field(default=None, max_length=128)
    secondary_intent: str | None = Field(default=None, max_length=128)
    summary: str | None = Field(default=None, max_length=10000)
    next_action: str | None = Field(default=None, max_length=256)


class ConversationUpdate(BaseModel):
    status: ConversationStatus | None = None
    current_state: str | None = Field(default=None, min_length=1, max_length=64)
    intent: str | None = Field(default=None, max_length=128)
    secondary_intent: str | None = Field(default=None, max_length=128)
    summary: str | None = Field(default=None, max_length=10000)
    next_action: str | None = Field(default=None, max_length=256)

    @model_validator(mode="after")
    def includes_change(self) -> "ConversationUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update.")
        return self


class ConversationResponse(BaseModel):
    id: UUID
    contact_id: UUID
    lead_id: UUID | None
    channel: ConversationChannel
    status: ConversationStatus
    current_state: str
    intent: str | None
    secondary_intent: str | None
    summary: str | None
    next_action: str | None
    created_at: datetime
    updated_at: datetime


class ConversationPage(BaseModel):
    items: list[ConversationResponse]
    limit: int
    offset: int


class MessageCreate(BaseModel):
    role: MessageRole
    content: str = Field(min_length=1, max_length=20000)
    message_type: str = Field(default="text", min_length=1, max_length=32)
    provider_message_id: str | None = Field(default=None, max_length=256)
    metadata_json: dict[str, object] = Field(default_factory=dict)


class MessageResponse(MessageCreate):
    id: UUID
    conversation_id: UUID
    created_at: datetime


class MessagePage(BaseModel):
    items: list[MessageResponse]
    limit: int
    offset: int
