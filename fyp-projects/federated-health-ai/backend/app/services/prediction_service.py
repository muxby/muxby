"""Clinical risk prediction served from the active global model."""

from __future__ import annotations

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Prediction, User
from app.schemas.api import PredictionInput
from app.services import audit_service, model_service
from fl_core.data import FEATURE_NAMES


class NoActiveModel(Exception):
    pass


def risk_level_for(probability: float) -> str:
    if probability < 0.33:
        return "low"
    if probability < 0.66:
        return "moderate"
    return "high"


def predict(db: Session, user: User, payload: PredictionInput) -> Prediction:
    loaded = model_service.load_inference_model(db)
    if loaded is None:
        raise NoActiveModel()
    model, scaler, version = loaded

    features = payload.model_dump()
    x = np.array([[features[name] for name in FEATURE_NAMES]], dtype=np.float64)
    probability = float(model.predict_proba(scaler.transform(x))[0])

    prediction = Prediction(
        user_id=user.id,
        model_version_id=version.id,
        features=features,
        probability=probability,
        diagnosis="high_risk" if probability >= 0.5 else "low_risk",
        risk_level=risk_level_for(probability),
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    audit_service.record(
        db, user.email, "prediction.create", f"prediction:{prediction.id}",
        f"model={version.version} p={probability:.3f}",
    )
    return prediction


def list_predictions(db: Session, user: User, limit: int = 200) -> list[Prediction]:
    stmt = (
        select(Prediction)
        .where(Prediction.user_id == user.id)
        .order_by(Prediction.id.desc())
        .limit(max(1, min(limit, 1000)))
    )
    return list(db.scalars(stmt))
