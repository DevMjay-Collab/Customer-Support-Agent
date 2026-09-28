from uuid import uuid4

from app.auth.security import hash_password, issue_session, parse_session, verify_password
from app.config import get_settings


def test_password_hashes_are_salted_and_verifiable() -> None:
    first = hash_password("long-test-password")
    second = hash_password("long-test-password")

    assert first != second
    assert verify_password("long-test-password", first)
    assert not verify_password("incorrect-password", first)


def test_session_cannot_be_tampered_with() -> None:
    token, _, _ = issue_session(uuid4(), get_settings())

    assert parse_session(token, get_settings()) is not None
    assert parse_session(f"{token}x", get_settings()) is None
