"""ORM entities for the platform."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    LargeBinary,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), default="researcher", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    predictions: Mapped[list["Prediction"]] = relationship(back_populates="user")


class Hospital(Base):
    __tablename__ = "hospitals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    region: Mapped[str] = mapped_column(String(128), nullable=False)
    data_size: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)
    status: Mapped[str] = mapped_column(String(16), default="online", nullable=False)
    # Deterministic per-hospital cohort characteristics for the simulation.
    data_seed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    risk_shift: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    updates: Mapped[list["ClientUpdate"]] = relationship(
        back_populates="hospital", cascade="all, delete-orphan"
    )


class TrainingRound(Base):
    """One federated training job (a sequence of FL rounds)."""

    __tablename__ = "training_rounds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)
    num_rounds: Mapped[int] = mapped_column(Integer, nullable=False)
    local_epochs: Mapped[int] = mapped_column(Integer, nullable=False)
    dp_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dp_epsilon: Mapped[float] = mapped_column(Float, default=8.0, nullable=False)
    secure_aggregation: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hospital_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    current_round: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    global_accuracy: Mapped[float | None] = mapped_column(Float, nullable=True)
    global_auc: Mapped[float | None] = mapped_column(Float, nullable=True)
    global_loss: Mapped[float | None] = mapped_column(Float, nullable=True)
    history: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    updates: Mapped[list["ClientUpdate"]] = relationship(
        back_populates="round", cascade="all, delete-orphan"
    )
    model_versions: Mapped[list["ModelVersion"]] = relationship(back_populates="round")


class ClientUpdate(Base):
    """Per-hospital, per-round contribution metadata (never raw data)."""

    __tablename__ = "client_updates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    round_id: Mapped[int] = mapped_column(
        ForeignKey("training_rounds.id", ondelete="CASCADE"), nullable=False, index=True
    )
    hospital_id: Mapped[int] = mapped_column(
        ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    num_samples: Mapped[int] = mapped_column(Integer, nullable=False)
    local_loss: Mapped[float] = mapped_column(Float, nullable=False)
    local_accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    local_auc: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    update_norm: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    round: Mapped[TrainingRound] = relationship(back_populates="updates")
    hospital: Mapped[Hospital] = relationship(back_populates="updates")


class ModelVersion(Base):
    """A stored global model checkpoint produced by a training round."""

    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    round_id: Mapped[int | None] = mapped_column(ForeignKey("training_rounds.id"), nullable=True)
    accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    auc: Mapped[float] = mapped_column(Float, nullable=False)
    loss: Mapped[float] = mapped_column(Float, nullable=False)
    num_parameters: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    weights: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    scaler: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    round: Mapped[TrainingRound | None] = relationship(back_populates="model_versions")


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    model_version_id: Mapped[int] = mapped_column(ForeignKey("model_versions.id"), nullable=False)
    features: Mapped[dict] = mapped_column(JSON, nullable=False)
    probability: Mapped[float] = mapped_column(Float, nullable=False)
    diagnosis: Mapped[str] = mapped_column(String(16), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user: Mapped[User] = relationship(back_populates="predictions")
    model_version: Mapped[ModelVersion] = relationship()


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_email: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    resource: Mapped[str] = mapped_column(String(128), nullable=False)
    detail: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
