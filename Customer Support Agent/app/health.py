from typing import Literal

from pydantic import BaseModel
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]


class ReadinessResponse(HealthResponse):
    database: Literal["ok", "unavailable"]
    redis: Literal["ok", "unavailable"]


async def database_is_ready(engine: AsyncEngine) -> bool:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception:
        return False
    return True


async def redis_is_ready(redis_url: str) -> bool:
    client = Redis.from_url(redis_url)
    try:
        return bool(await client.ping())
    except Exception:
        return False
    finally:
        await client.aclose()

