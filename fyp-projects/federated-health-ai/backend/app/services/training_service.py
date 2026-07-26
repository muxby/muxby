"""Runs federated training jobs and persists their progress.

The job executes in a worker thread with its own DB session; progress is
written to the ``training_rounds`` / ``client_updates`` tables as it happens,
so the WebSocket endpoint (and any poller) can stream live state without
cross-thread asyncio plumbing.
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.models import Hospital, TrainingRound
from app.schemas.api import RoundCreate
from app.services import audit_service, model_service
from fl_core.data import FeatureScaler, generate_patients, train_test_split
from fl_core.simulation import FederatedSimulation, RoundConfig


class RoundNotFound(Exception):
    pass


class InvalidRoundRequest(Exception):
    pass


def list_rounds(db: Session) -> list[TrainingRound]:
    return list(db.scalars(select(TrainingRound).order_by(TrainingRound.id.desc())))


def get_round(db: Session, round_id: int) -> TrainingRound:
    rnd = db.get(TrainingRound, round_id)
    if rnd is None:
        raise RoundNotFound(round_id)
    return rnd


def create_round(db: Session, payload: RoundCreate, actor_email: str, user_id: int | None) -> TrainingRound:
    hospitals = [db.get(Hospital, hid) for hid in payload.hospital_ids]
    missing = [hid for hid, h in zip(payload.hospital_ids, hospitals) if h is None]
    if missing:
        raise InvalidRoundRequest(f"unknown hospital ids: {missing}")
    offline = [h.name for h in hospitals if h is not None and h.status != "online"]
    if offline:
        raise InvalidRoundRequest(f"hospitals offline: {offline}")

    rnd = TrainingRound(
        status="pending",
        num_rounds=payload.num_rounds,
        local_epochs=payload.local_epochs,
        dp_enabled=payload.dp_enabled,
        dp_epsilon=payload.dp_epsilon,
        secure_aggregation=payload.secure_aggregation,
        hospital_ids=sorted(set(payload.hospital_ids)),
        created_by=user_id,
    )
    db.add(rnd)
    db.commit()
    db.refresh(rnd)
    audit_service.record(
        db, actor_email, "round.create", f"round:{rnd.id}",
        f"hospitals={rnd.hospital_ids} rounds={rnd.num_rounds} dp={rnd.dp_enabled}",
    )
    return rnd


def cancel_round(db: Session, round_id: int, actor_email: str) -> TrainingRound:
    rnd = get_round(db, round_id)
    if rnd.status in ("pending", "running"):
        rnd.status = "cancelled"
        db.commit()
        db.refresh(rnd)
        audit_service.record(db, actor_email, "round.cancel", f"round:{round_id}")
    return rnd


# ---------------------------------------------------------------------------
def execute_round(round_id: int, session_factory: sessionmaker) -> None:
    """Run the federated job for ``round_id`` to completion (worker entry)."""
    db = session_factory()
    try:
        rnd = db.get(TrainingRound, round_id)
        if rnd is None or rnd.status == "cancelled":
            return
        rnd.status = "running"
        db.commit()
        _train(db, rnd)
    except Exception as exc:  # noqa: BLE001 — job boundary: persist any failure
        db.rollback()
        rnd = db.get(TrainingRound, round_id)
        if rnd is not None:
            rnd.status = "failed"
            rnd.error = f"{type(exc).__name__}: {exc}"
            rnd.completed_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()


def start_round_async(round_id: int, session_factory: sessionmaker) -> threading.Thread:
    thread = threading.Thread(
        target=execute_round, args=(round_id, session_factory), daemon=True, name=f"fl-round-{round_id}"
    )
    thread.start()
    return thread


def _train(db: Session, rnd: TrainingRound) -> None:
    settings = get_settings()
    hospitals = [db.get(Hospital, hid) for hid in rnd.hospital_ids]
    hospitals = [h for h in hospitals if h is not None]

    # Public reference cohort: fits the scaler and provides held-out
    # evaluation without touching any hospital's private shard.
    X_ref, y_ref = generate_patients(settings.cohort_test_samples * 2, seed=settings.cohort_seed)
    scaler = FeatureScaler.fit(X_ref)
    _, _, X_test, y_test = train_test_split(
        scaler.transform(X_ref), y_ref, test_fraction=0.5, seed=settings.cohort_seed
    )

    client_datasets = {}
    for h in hospitals:
        Xh, yh = generate_patients(h.data_size, seed=h.data_seed, risk_shift=h.risk_shift)
        client_datasets[h.id] = (scaler.transform(Xh), yh)

    config = RoundConfig(
        num_rounds=rnd.num_rounds,
        local_epochs=rnd.local_epochs,
        dp_enabled=rnd.dp_enabled,
        dp_epsilon=rnd.dp_epsilon,
        secure_aggregation=rnd.secure_aggregation,
        seed=settings.cohort_seed + rnd.id,
    )

    round_id = rnd.id

    def progress(event: dict) -> None:
        _persist_progress(db, round_id, event)

    def cancelled() -> bool:
        db.expire_all()
        current = db.get(TrainingRound, round_id)
        return current is None or current.status == "cancelled"

    sim = FederatedSimulation(
        client_datasets,
        (X_test, y_test),
        config,
        progress_cb=progress,
        cancel_cb=cancelled,
    )
    result = sim.run()

    rnd = db.get(TrainingRound, round_id)
    if rnd is None:
        return
    if result.cancelled:
        rnd.status = "cancelled"
    else:
        rnd.status = "completed"
        model_service.store_model_version(db, rnd, result.final_params, scaler, result.final_eval)
    if result.final_eval is not None:
        rnd.global_accuracy = result.final_eval.accuracy
        rnd.global_auc = result.final_eval.auc
        rnd.global_loss = result.final_eval.loss
    rnd.completed_at = datetime.now(timezone.utc)
    db.commit()


def _persist_progress(db: Session, round_id: int, event: dict) -> None:
    from app.models import ClientUpdate  # local import avoids cycle at module load

    rnd = db.get(TrainingRound, round_id)
    if rnd is None:
        return
    if event["type"] == "round_progress":
        rnd.current_round = event["round_number"]
        rnd.history = [
            *rnd.history,
            {
                "round_number": event["round_number"],
                "accuracy": event["accuracy"],
                "auc": event["auc"],
                "loss": event["loss"],
            },
        ]
        rnd.global_accuracy = event["accuracy"]
        rnd.global_auc = event["auc"]
        rnd.global_loss = event["loss"]
    elif event["type"] == "client_update":
        db.add(
            ClientUpdate(
                round_id=round_id,
                hospital_id=event["client_id"],
                round_number=event["round_number"],
                num_samples=event.get("num_samples", 0),
                local_loss=event["local_loss"],
                local_accuracy=event["local_accuracy"],
                local_auc=event.get("local_auc", 0.5),
                update_norm=event.get("update_norm", 0.0),
            )
        )
    db.commit()
