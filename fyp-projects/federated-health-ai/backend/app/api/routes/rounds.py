from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
import app.db.session as db_session
from app.db.session import get_db
from app.models import Hospital, User
from app.schemas.api import ClientUpdateOut, RoundCreate, RoundDetail, RoundOut
from app.services import training_service
from app.services.training_service import InvalidRoundRequest, RoundNotFound

router = APIRouter(prefix="/rounds", tags=["rounds"])


@router.get("", response_model=list[RoundOut])
def list_rounds(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return training_service.list_rounds(db)


@router.post("", response_model=RoundOut, status_code=status.HTTP_201_CREATED)
def create_round(
    payload: RoundCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        rnd = training_service.create_round(db, payload, user.email, user.id)
    except InvalidRoundRequest as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    training_service.start_round_async(rnd.id, db_session.SessionLocal)
    return rnd


@router.get("/{round_id}", response_model=RoundDetail)
def get_round(round_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    try:
        rnd = training_service.get_round(db, round_id)
    except RoundNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Round not found")
    return _round_detail(db, rnd)


@router.post("/{round_id}/cancel", response_model=RoundOut)
def cancel_round(
    round_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        return training_service.cancel_round(db, round_id, user.email)
    except RoundNotFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Round not found")


def _round_detail(db: Session, rnd) -> RoundDetail:
    detail = RoundDetail.model_validate(rnd)
    names = {h.id: h.name for h in db.query(Hospital).all()}
    updates = []
    for u in sorted(rnd.updates, key=lambda x: (x.round_number, x.hospital_id)):
        out = ClientUpdateOut.model_validate(u)
        out.hospital_name = names.get(u.hospital_id, f"hospital-{u.hospital_id}")
        updates.append(out)
    detail.updates = updates
    return detail
