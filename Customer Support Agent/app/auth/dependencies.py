from datetime import UTC, datetime

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import AuthSession, User
from app.auth.router import COOKIE_NAME
from app.auth.security import parse_session, token_fingerprint
from app.config import get_settings
from app.db import get_db_session


async def get_current_owner(
    request: Request, session: AsyncSession = Depends(get_db_session)
) -> User:
    token = request.cookies.get(COOKIE_NAME)
    parsed = parse_session(token, get_settings()) if token else None
    if not parsed or token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    session_record = await session.get(AuthSession, parsed[0])
    if (
        session_record is None
        or session_record.user_id != parsed[1]
        or session_record.token_hash != token_fingerprint(token)
        or session_record.revoked_at is not None
        or session_record.expires_at <= datetime.now(UTC)
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is invalid.")
    user = await session.get(User, parsed[1])
    if user is None or user.status != "active":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is invalid.")
    return user
