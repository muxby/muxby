"""Append-only audit trail of every state-changing action."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuditEvent


def record(db: Session, actor_email: str, action: str, resource: str, detail: str = "") -> AuditEvent:
    event = AuditEvent(actor_email=actor_email, action=action, resource=resource, detail=detail)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_events(db: Session, limit: int = 100) -> list[AuditEvent]:
    limit = max(1, min(limit, 1000))
    stmt = select(AuditEvent).order_by(AuditEvent.id.desc()).limit(limit)
    return list(db.scalars(stmt))
