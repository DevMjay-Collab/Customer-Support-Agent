from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.agent.router import router as agent_router
from app.auth.router import router as auth_router
from app.auth.service import bootstrap_owner
from app.config import get_settings
from app.configuration.router import router as configuration_router
from app.db import SessionLocal, engine
from app.health import HealthResponse, ReadinessResponse, database_is_ready, redis_is_ready
from app.logging import configure_logging
from app.operations.router import router as operations_router

settings = get_settings()
configure_logging(settings.log_level)
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    async with SessionLocal() as session:
        await bootstrap_owner(session, settings)
    logger.info("application.started", environment=settings.app_env)
    yield
    await engine.dispose()
    logger.info("application.stopped")


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(configuration_router)
app.include_router(agent_router)
app.include_router(operations_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


@app.middleware("http")
async def request_context(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    structlog.contextvars.bind_contextvars(request_id=request_id)
    try:
        response = await call_next(request)
    finally:
        structlog.contextvars.unbind_contextvars("request_id")
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health", response_model=HealthResponse, tags=["operational"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get(
    "/ready",
    response_model=ReadinessResponse,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ReadinessResponse}},
    tags=["operational"],
)
async def readiness() -> JSONResponse:
    database_ok = await database_is_ready(engine)
    redis_ok = await redis_is_ready(settings.redis_url)
    is_ready = database_ok and redis_ok
    body = ReadinessResponse(
        status="ok" if is_ready else "degraded",
        database="ok" if database_ok else "unavailable",
        redis="ok" if redis_ok else "unavailable",
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        content=body.model_dump(),
    )
