from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.security import hash_password
from app.config import Settings


async def bootstrap_owner(session: AsyncSession, settings: Settings) -> None:
    if not settings.owner_bootstrap_email or not settings.owner_bootstrap_password:
        return
    count = await session.scalar(select(func.count()).select_from(User))
    if count:
        return
    password = settings.owner_bootstrap_password.get_secret_value()
    if len(password) < 12:
        raise RuntimeError("OWNER_BOOTSTRAP_PASSWORD must be at least 12 characters.")
    session.add(
        User(
            email=settings.owner_bootstrap_email.strip().lower(),
            password_hash=hash_password(password),
            status="active",
        )
    )
    await session.commit()
