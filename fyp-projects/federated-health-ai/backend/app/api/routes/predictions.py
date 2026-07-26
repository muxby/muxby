from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import User
from app.schemas.api import PredictionInput, PredictionOut
from app.services import prediction_service
from app.services.prediction_service import NoActiveModel

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("", response_model=PredictionOut, status_code=status.HTTP_201_CREATED)
def create_prediction(
    payload: PredictionInput,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        prediction = prediction_service.predict(db, user, payload)
    except NoActiveModel:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No active model — complete a training round first",
        )
    return _to_out(prediction)


@router.get("", response_model=list[PredictionOut])
def list_predictions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return [_to_out(p) for p in prediction_service.list_predictions(db, user)]


def _to_out(p) -> PredictionOut:
    return PredictionOut(
        id=p.id,
        probability=p.probability,
        diagnosis=p.diagnosis,
        risk_level=p.risk_level,
        model_version=p.model_version.version,
        features=p.features,
        created_at=p.created_at,
    )
