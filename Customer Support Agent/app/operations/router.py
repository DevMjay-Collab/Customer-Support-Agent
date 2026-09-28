from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_owner
from app.auth.models import User
from app.core.models import Contact, Conversation, Lead, Message
from app.db import get_db_session
from app.operations.audit import record_audit
from app.operations.schemas import (
    ContactCreate,
    ContactPage,
    ContactResponse,
    ContactUpdate,
    ConversationCreate,
    ConversationPage,
    ConversationResponse,
    ConversationUpdate,
    LeadCreate,
    LeadPage,
    LeadResponse,
    LeadStatus,
    MessageCreate,
    MessagePage,
    MessageResponse,
)

router = APIRouter(prefix="/api/v1", tags=["customer operations"])


def not_found(resource: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found.")


def contact_response(contact: Contact) -> ContactResponse:
    return ContactResponse.model_validate(contact, from_attributes=True)


def lead_response(lead: Lead) -> LeadResponse:
    return LeadResponse.model_validate(lead, from_attributes=True)


def conversation_response(conversation: Conversation) -> ConversationResponse:
    return ConversationResponse.model_validate(conversation, from_attributes=True)


def message_response(message: Message) -> MessageResponse:
    return MessageResponse.model_validate(message, from_attributes=True)


@router.post("/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    payload: ContactCreate,
    owner: User = Depends(get_current_owner),
    session: AsyncSession = Depends(get_db_session),
) -> ContactResponse:
    contact = Contact(**payload.model_dump())
    session.add(contact)
    await session.flush()
    record_audit(
        session,
        event_type="contact.created",
        actor_id=owner.id,
        resource_type="contact",
        resource_id=contact.id,
    )
    await session.commit()
    await session.refresh(contact)
    return contact_response(contact)


@router.get("/contacts", response_model=ContactPage)
async def list_contacts(
    search: str | None = Query(default=None, min_length=1, max_length=200),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(get_current_owner),
    session: AsyncSession = Depends(get_db_session),
) -> ContactPage:
    statement = select(Contact).order_by(Contact.updated_at.desc(), Contact.id).limit(limit).offset(offset)
    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                Contact.name.ilike(pattern),
                Contact.phone.ilike(pattern),
                Contact.email.ilike(pattern),
                Contact.company.ilike(pattern),
            )
        )
    contacts = (await session.scalars(statement)).all()
    return ContactPage(items=[contact_response(contact) for contact in contacts], limit=limit, offset=offset)


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: UUID,
    _: User = Depends(get_current_owner),
    session: AsyncSession = Depends(get_db_session),
) -> ContactResponse:
    contact = await session.get(Contact, contact_id)
    if contact is None:
        raise not_found("Contact")
    return contact_response(contact)


@router.patch("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: UUID,
    payload: ContactUpdate,
    owner: User = Depends(get_current_owner),
    session: AsyncSession = Depends(get_db_session),
) -> ContactResponse:
    contact = await session.get(Contact, contact_id)
    if contact is None:
        raise not_found("Contact")
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(contact, field, value)
    record_audit(
        session,
        event_type="contact.updated",
        actor_id=owner.id,
        resource_type="contact",
        resource_id=contact.id,
        metadata={"changed_fields": sorted(changes)},
    )
    await session.commit()
    await session.refresh(contact)
    return contact_response(contact)


@router.post("/contacts/{contact_id}/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    contact_id: UUID,
    payload: LeadCreate,
    owner: User = Depends(get_current_owner),
    session: AsyncSession = Depends(get_db_session),
) -> LeadResponse:
    if await session.get(Contact, contact_id) is None:
        raise not_found("Contact")
    lead = Lead(contact_id=contact_id, **payload.model_dump())
    session.add(lead)
    await session.flush()
    record_audit(
        session,
        event_type="lead.created",
        actor_id=owner.id,
        resource_type="lead",
        resource_id=lead.id,
        metadata={"contact_id": str(contact_id)},
    )
    await session.commit()
    await session.refresh(lead)
    return lead_response(lead)


@router.get("/leads", response_model=LeadPage)
async def list_leads(
    contact_id: UUID | None = None,
    lead_status: LeadStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(get_current_owner),
    session: AsyncSession = Depends(get_db_session),
) -> LeadPage:
    statement = select(Lead).order_by(Lead.updated_at.desc(), Lead.id).limit(limit).offset(offset)
    if contact_id:
        statement = statement.where(Lead.contact_id == contact_id)
    if lead_status:
        statement = statement.where(Lead.status == lead_status)
    leads = (await session.scalars(statement)).all()
    return LeadPage(items=[lead_response(lead) for lead in leads], limit=limit, offset=offset)


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    owner: User = Depends(get_current_owner),
    session: AsyncSession = Depends(get_db_session),
) -> ConversationResponse:
    if await session.get(Contact, payload.contact_id) is None:
        raise not_found("Contact")
    if payload.lead_id is not None:
        lead = await session.get(Lead, payload.lead_id)
        if lead is None:
            raise not_found("Lead")
        if lead.contact_id != payload.contact_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="The lead must belong to the conversation contact.",
            )
    conversation = Conversation(status="active", **payload.model_dump())
    session.add(conversation)
    await session.flush()
    record_audit(
        session,
        event_type="conversation.created",
        actor_id=owner.id,
        resource_type="conversation",
        resource_id=conversation.id,
        metadata={"channel": conversation.channel},
    )
    await session.commit()
    await session.refresh(conversation)
    return conversation_response(conversation)


@router.get("/conversations", response_model=ConversationPage)
async def list_conversations(
    contact_id: UUID | None = None,
    conversation_status: str | None = Query(default=None, alias="status", pattern="^(active|waiting|resolved|closed)$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(get_current_owner),
    session: AsyncSession = Depends(get_db_session),
) -> ConversationPage:
    statement = select(Conversation).order_by(Conversation.updated_at.desc(), Conversation.id).limit(limit).offset(offset)
    if contact_id:
        statement = statement.where(Conversation.contact_id == contact_id)
    if conversation_status:
        statement = statement.where(Conversation.status == conversation_status)
    conversations = (await session.scalars(statement)).all()
    return ConversationPage(
        items=[conversation_response(conversation) for conversation in conversations],
        limit=limit,
        offset=offset,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    _: User = Depends(get_current_owner),
    session: AsyncSession = Depends(get_db_session),
) -> ConversationResponse:
    conversation = await session.get(Conversation, conversation_id)
    if conversation is None:
        raise not_found("Conversation")
    return conversation_response(conversation)


@router.patch("/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: UUID,
    payload: ConversationUpdate,
    owner: User = Depends(get_current_owner),
    session: AsyncSession = Depends(get_db_session),
) -> ConversationResponse:
    conversation = await session.get(Conversation, conversation_id)
    if conversation is None:
        raise not_found("Conversation")
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(conversation, field, value)
    record_audit(
        session,
        event_type="conversation.updated",
        actor_id=owner.id,
        resource_type="conversation",
        resource_id=conversation.id,
        metadata={"changed_fields": sorted(changes)},
    )
    await session.commit()
    await session.refresh(conversation)
    return conversation_response(conversation)


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_message(
    conversation_id: UUID,
    payload: MessageCreate,
    owner: User = Depends(get_current_owner),
    session: AsyncSession = Depends(get_db_session),
) -> MessageResponse:
    if await session.get(Conversation, conversation_id) is None:
        raise not_found("Conversation")
    message = Message(conversation_id=conversation_id, **payload.model_dump())
    session.add(message)
    await session.flush()
    record_audit(
        session,
        event_type="message.created",
        actor_id=owner.id,
        resource_type="message",
        resource_id=message.id,
        metadata={"conversation_id": str(conversation_id), "role": message.role},
    )
    await session.commit()
    await session.refresh(message)
    return message_response(message)


@router.get("/conversations/{conversation_id}/messages", response_model=MessagePage)
async def list_messages(
    conversation_id: UUID,
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    _: User = Depends(get_current_owner),
    session: AsyncSession = Depends(get_db_session),
) -> MessagePage:
    if await session.get(Conversation, conversation_id) is None:
        raise not_found("Conversation")
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at, Message.id)
        .limit(limit)
        .offset(offset)
    )
    messages = (await session.scalars(statement)).all()
    return MessagePage(items=[message_response(message) for message in messages], limit=limit, offset=offset)
