"""Hospital (federated client) management."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ClientUpdate, Hospital
from app.schemas.api import HospitalCreate, HospitalUpdate
from app.services import audit_service


class HospitalNameTaken(Exception):
    pass


class HospitalNotFound(Exception):
    pass


def list_hospitals(db: Session) -> list[Hospital]:
    return list(db.scalars(select(Hospital).order_by(Hospital.id)))


def get_hospital(db: Session, hospital_id: int) -> Hospital:
    hospital = db.get(Hospital, hospital_id)
    if hospital is None:
        raise HospitalNotFound(hospital_id)
    return hospital


def create_hospital(db: Session, payload: HospitalCreate, actor_email: str) -> Hospital:
    if db.scalar(select(Hospital).where(Hospital.name == payload.name)) is not None:
        raise HospitalNameTaken(payload.name)
    max_id = db.scalar(select(Hospital.id).order_by(Hospital.id.desc()).limit(1)) or 0
    hospital = Hospital(
        name=payload.name,
        region=payload.region,
        data_size=payload.data_size,
        risk_shift=payload.risk_shift,
        # Distinct deterministic seed per hospital so shards never overlap.
        data_seed=1000 + max_id + 1,
        status="online",
    )
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    audit_service.record(db, actor_email, "hospital.create", f"hospital:{hospital.id}", payload.name)
    return hospital


def update_hospital(db: Session, hospital_id: int, payload: HospitalUpdate, actor_email: str) -> Hospital:
    hospital = get_hospital(db, hospital_id)
    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if "name" in changes and changes["name"] != hospital.name:
        if db.scalar(select(Hospital).where(Hospital.name == changes["name"])) is not None:
            raise HospitalNameTaken(changes["name"])
    for field, value in changes.items():
        setattr(hospital, field, value)
    db.commit()
    db.refresh(hospital)
    audit_service.record(db, actor_email, "hospital.update", f"hospital:{hospital.id}", str(changes))
    return hospital


def delete_hospital(db: Session, hospital_id: int, actor_email: str) -> None:
    hospital = get_hospital(db, hospital_id)
    db.delete(hospital)
    db.commit()
    audit_service.record(db, actor_email, "hospital.delete", f"hospital:{hospital_id}", hospital.name)


def hospital_metrics(db: Session, hospital_id: int) -> list[dict]:
    """Latest local accuracy/loss per training round for this hospital."""
    get_hospital(db, hospital_id)
    stmt = (
        select(ClientUpdate)
        .where(ClientUpdate.hospital_id == hospital_id)
        .order_by(ClientUpdate.round_id, ClientUpdate.round_number)
    )
    latest_per_round: dict[int, ClientUpdate] = {}
    for update in db.scalars(stmt):
        latest_per_round[update.round_id] = update
    return [
        {
            "round_id": round_id,
            "accuracy": u.local_accuracy,
            "auc": u.local_auc,
            "loss": u.local_loss,
        }
        for round_id, u in sorted(latest_per_round.items())
    ]
