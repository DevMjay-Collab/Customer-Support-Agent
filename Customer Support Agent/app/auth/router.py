from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import AuthSession, User
from app.auth.schemas import AuthenticatedUser, LoginRequest
from app.auth.security import issue_session, parse_session, token_fingerprint, verify_password
from app.config import get_settings
from app.db import get_db_session

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
COOKIE_NAME = "hmc_session"


@router.post("/login", response_model=AuthenticatedUser)
async def login(payload: LoginRequest, response: Response, session: AsyncSession = Depends(get_db_session)) -> AuthenticatedUser:
    user = await session.scalar(select(User).where(User.email == payload.email.strip().lower()))
    if user is None or user.status != "active" or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    token, session_id, expires_at = issue_session(user.id, get_settings())
    session.add(AuthSession(id=session_id, user_id=user.id, token_hash=token_fingerprint(token), expires_at=expires_at))
    await session.commit()
    response.set_cookie(
        COOKIE_NAME, token, httponly=True, secure=get_settings().app_env == "production",
        samesite="lax", max_age=int((expires_at - datetime.now(UTC)).total_seconds()), path="/"
    )
    return AuthenticatedUser(id=str(user.id), email=user.email)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, response: Response, session: AsyncSession = Depends(get_db_session)) -> Response:
    token = request.cookies.get(COOKIE_NAME)
    parsed = parse_session(token, get_settings()) if token else None
    if parsed:
        assert token is not None
        session_record = await session.get(AuthSession, parsed[0])
        if session_record and session_record.token_hash == token_fingerprint(token):
            session_record.revoked_at = datetime.now(UTC)
            await session.commit()
    response.delete_cookie(COOKIE_NAME, path="/")
    return response


@router.post("/password-reset/request", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
async def password_reset_request() -> None:
    raise HTTPException(status_code=503, detail="Password-reset email delivery is not configured.")
