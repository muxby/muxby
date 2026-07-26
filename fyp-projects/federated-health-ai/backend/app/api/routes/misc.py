"""Audit log and dashboard statistics."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Hospital, ModelVersion, Prediction, TrainingRound, User
from app.schemas.api import AuditEventOut, RoundOut, StatsOverview
from app.services import audit_service

router = APIRouter(tags=["misc"])


@router.get("/audit", response_model=list[AuditEventOut])
def audit_log(
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return audit_service.list_events(db, limit)


@router.get("/stats/overview", response_model=StatsOverview)
def stats_overview(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    hospitals = db.scalar(select(func.count(Hospital.id))) or 0
    online = db.scalar(select(func.count(Hospital.id)).where(Hospital.status == "online")) or 0
    completed = (
        db.scalar(select(func.count(TrainingRound.id)).where(TrainingRound.status == "completed")) or 0
    )
    predictions = db.scalar(select(func.count(Prediction.id))) or 0
    active = db.scalar(select(ModelVersion).where(ModelVersion.is_active.is_(True)))
    last = db.scalar(select(TrainingRound).order_by(TrainingRound.id.desc()).limit(1))
    return StatsOverview(
        hospitals=hospitals,
        hospitals_online=online,
        rounds_completed=completed,
        active_model_accuracy=active.accuracy if active else None,
        active_model_auc=active.auc if active else None,
        predictions_made=predictions,
        last_round=RoundOut.model_validate(last) if last else None,
    )
