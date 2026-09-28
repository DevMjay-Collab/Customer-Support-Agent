from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.models import AgentConfig
from app.auth.dependencies import get_current_owner
from app.auth.models import User
from app.db import get_db_session

router = APIRouter(prefix="/api/v1/settings", tags=["agent configuration"])


class AgentConfigPayload(BaseModel):
    name: str = Field(default="HMC Support Agent", min_length=1, max_length=200)
    status: str = Field(default="active", pattern="^(active|inactive)$")
    system_instructions: str = Field(default="", max_length=20000)
    personality: str | None = Field(default=None, max_length=4000)
    language: str = Field(default="en", min_length=2, max_length=32)
    voice_provider: str | None = Field(default=None, max_length=64)
    voice_id: str | None = Field(default=None, max_length=256)
    allowed_tools_json: list[str] = Field(default_factory=list)
    escalation_rules_json: dict[str, object] = Field(default_factory=dict)
    lead_scoring_config_json: dict[str, object] = Field(default_factory=dict)


@router.get("/agent", response_model=AgentConfigPayload)
async def get_agent_config(
    _: User = Depends(get_current_owner), session: AsyncSession = Depends(get_db_session)
) -> AgentConfigPayload:
    config = await session.scalar(select(AgentConfig))
    if config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent configuration not found.")
    return AgentConfigPayload.model_validate(config, from_attributes=True)


@router.patch("/agent", response_model=AgentConfigPayload)
async def update_agent_config(
    payload: AgentConfigPayload,
    _: User = Depends(get_current_owner),
    session: AsyncSession = Depends(get_db_session),
) -> AgentConfigPayload:
    config = await session.scalar(select(AgentConfig))
    if config is None:
        config = AgentConfig(**payload.model_dump())
        session.add(config)
    else:
        for field, value in payload.model_dump().items():
            setattr(config, field, value)
    await session.commit()
    await session.refresh(config)
    return AgentConfigPayload.model_validate(config, from_attributes=True)
