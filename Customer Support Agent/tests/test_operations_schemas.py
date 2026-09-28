import pytest
from app.operations.schemas import ContactCreate, ContactUpdate, ConversationCreate, MessageCreate
from pydantic import ValidationError


def test_contact_requires_identifying_information() -> None:
    with pytest.raises(ValidationError, match="identifying contact field"):
        ContactCreate()

    contact = ContactCreate(name="Avery Customer", metadata_json={"source": "web"})

    assert contact.name == "Avery Customer"
    assert contact.metadata_json == {"source": "web"}


def test_contact_update_requires_a_change() -> None:
    with pytest.raises(ValidationError, match="at least one field"):
        ContactUpdate()

    assert ContactUpdate(email=None).model_dump(exclude_unset=True) == {"email": None}


def test_conversation_and_message_inputs_are_constrained() -> None:
    with pytest.raises(ValidationError):
        ConversationCreate(contact_id="1f81f5d3-2f99-4900-a602-49b85011ddce", channel="telegram")

    with pytest.raises(ValidationError):
        MessageCreate(role="customer", content="")
