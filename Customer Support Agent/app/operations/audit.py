from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models import AuditLog


def record_audit(
    session: AsyncSession,
    *,
    event_type: str,
    actor_id: UUID,
    resource_type: str,
    resource_id: UUID,
    metadata: dict[str, object] | None = None,
) -> None:
    """Append a non-sensitive record of an authenticated durable change."""
    session.add(
        AuditLog(
            event_type=event_type,
            actor_type="owner",
            actor_id=actor_id,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata_json=metadata or {},
        )
    )
