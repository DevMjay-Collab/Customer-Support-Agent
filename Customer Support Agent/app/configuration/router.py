from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_owner
from app.auth.models import User
from app.configuration.models import BusinessSettings
from app.configuration.schemas import BusinessSettingsResponse, BusinessSettingsUpdate
from app.db import get_db_session

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


def serialize(settings: BusinessSettings) -> BusinessSettingsResponse:
    return BusinessSettingsResponse(
        business_name=settings.business_name,
        business_description=settings.business_description,
        website=settings.website,
        timezone=settings.timezone,
        business_hours_json=settings.business_hours_json,
        support_email=settings.support_email,
        support_phone=settings.support_phone,
        default_calendar_id=settings.default_calendar_id,
    )


@router.get("/business", response_model=BusinessSettingsResponse)
async def get_business_settings(
    _: User = Depends(get_current_owner),
    session: AsyncSession = Depends(get_db_session),
) -> BusinessSettingsResponse:
    settings = await session.scalar(select(BusinessSettings))
    if settings is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business settings not configured.")
    return serialize(settings)


@router.patch("/business", response_model=BusinessSettingsResponse)
async def update_business_settings(
    payload: BusinessSettingsUpdate,
    _: User = Depends(get_current_owner),
    session: AsyncSession = Depends(get_db_session),
) -> BusinessSettingsResponse:
    settings = await session.scalar(select(BusinessSettings))
    if settings is None:
        settings = BusinessSettings(business_name=payload.business_name or "HMC")
        session.add(settings)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
    await session.commit()
    await session.refresh(settings)
    return serialize(settings)
