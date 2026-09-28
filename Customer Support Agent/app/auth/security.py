import base64
import hashlib
import hmac
import json
import os
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from app.config import Settings

SESSION_TTL = timedelta(hours=8)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return "scrypt$16384$8$1$%s$%s" % (
        base64.urlsafe_b64encode(salt).decode(),
        base64.urlsafe_b64encode(digest).decode(),
    )


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, n, r, p, salt, digest = stored.split("$")
        calculated = hashlib.scrypt(
            password.encode(),
            salt=base64.urlsafe_b64decode(salt),
            n=int(n),
            r=int(r),
            p=int(p),
        )
    except (ValueError, TypeError):
        return False
    return algorithm == "scrypt" and hmac.compare_digest(
        calculated, base64.urlsafe_b64decode(digest)
    )


def issue_session(user_id: UUID, settings: Settings) -> tuple[str, UUID, datetime]:
    session_id = uuid4()
    expires_at = datetime.now(UTC) + SESSION_TTL
    payload = {"sid": str(session_id), "uid": str(user_id), "exp": int(expires_at.timestamp())}
    encoded = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode()
    signature = hmac.new(
        settings.app_secret_key.get_secret_value().encode(), encoded.encode(), hashlib.sha256
    ).hexdigest()
    return f"{encoded}.{signature}", session_id, expires_at


def parse_session(token: str, settings: Settings) -> tuple[UUID, UUID] | None:
    try:
        encoded, received_signature = token.rsplit(".", 1)
        expected_signature = hmac.new(
            settings.app_secret_key.get_secret_value().encode(), encoded.encode(), hashlib.sha256
        ).hexdigest()
        payload = json.loads(base64.urlsafe_b64decode(encoded))
        if not hmac.compare_digest(received_signature, expected_signature) or payload["exp"] < datetime.now(UTC).timestamp():
            return None
        return UUID(payload["sid"]), UUID(payload["uid"])
    except (ValueError, KeyError, json.JSONDecodeError):
        return None


def token_fingerprint(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
