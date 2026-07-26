"""Model registry: stores, lists, and activates global model checkpoints."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ModelVersion, TrainingRound
from app.services import audit_service
from fl_core.data import FeatureScaler
from fl_core.nn import MLP
from fl_core.data import NUM_FEATURES
from fl_core.serialization import params_from_bytes, params_to_bytes
from fl_core.trainer import EvalResult


class ModelNotFound(Exception):
    pass


def list_models(db: Session) -> list[ModelVersion]:
    return list(db.scalars(select(ModelVersion).order_by(ModelVersion.id.desc())))


def get_model(db: Session, model_id: int) -> ModelVersion:
    model = db.get(ModelVersion, model_id)
    if model is None:
        raise ModelNotFound(model_id)
    return model


def get_active_model(db: Session) -> ModelVersion | None:
    return db.scalar(select(ModelVersion).where(ModelVersion.is_active.is_(True)))


def store_model_version(
    db: Session,
    rnd: TrainingRound,
    params: list,
    scaler: FeatureScaler,
    final_eval: EvalResult | None,
) -> ModelVersion:
    count = db.scalar(select(func.count(ModelVersion.id))) or 0
    model = MLP(NUM_FEATURES)
    model.set_parameters(params)
    version = ModelVersion(
        version=f"v{count + 1}.0",
        round_id=rnd.id,
        accuracy=final_eval.accuracy if final_eval else 0.0,
        auc=final_eval.auc if final_eval else 0.5,
        loss=final_eval.loss if final_eval else 0.0,
        num_parameters=model.num_parameters(),
        is_active=False,
        weights=params_to_bytes(params),
        scaler=params_to_bytes(scaler.to_arrays()),
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    # Auto-activate when it is the first model or beats the active one on AUC.
    active = get_active_model(db)
    if active is None or version.auc >= active.auc:
        activate_model(db, version.id, actor_email="system")
        db.refresh(version)
    return version


def activate_model(db: Session, model_id: int, actor_email: str) -> ModelVersion:
    model = get_model(db, model_id)
    for other in db.scalars(select(ModelVersion).where(ModelVersion.is_active.is_(True))):
        other.is_active = False
    model.is_active = True
    db.commit()
    db.refresh(model)
    audit_service.record(db, actor_email, "model.activate", f"model:{model.version}")
    return model


def load_inference_model(db: Session) -> tuple[MLP, FeatureScaler, ModelVersion] | None:
    """Materialise the active checkpoint for prediction serving."""
    version = get_active_model(db)
    if version is None:
        return None
    model = MLP(NUM_FEATURES)
    model.set_parameters(params_from_bytes(version.weights))
    scaler = FeatureScaler.from_arrays(params_from_bytes(version.scaler))
    return model, scaler, version
