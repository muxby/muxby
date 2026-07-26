"""Pydantic request/response schemas for the REST API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---- auth ----------------------------------------------------------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)


class UserOut(ORMModel):
    id: int
    email: str
    full_name: str
    role: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---- hospitals -----------------------------------------------------------
class HospitalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    region: str = Field(min_length=1, max_length=128)
    data_size: int = Field(ge=50, le=100_000, default=1000)
    risk_shift: float = Field(ge=-2.0, le=2.0, default=0.0)


class HospitalUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    region: str | None = Field(default=None, min_length=1, max_length=128)
    data_size: int | None = Field(default=None, ge=50, le=100_000)
    status: str | None = Field(default=None, pattern="^(online|offline)$")


class HospitalOut(ORMModel):
    id: int
    name: str
    region: str
    data_size: int
    status: str
    created_at: datetime


class HospitalMetric(BaseModel):
    round_id: int
    accuracy: float
    auc: float
    loss: float


class HospitalDetail(HospitalOut):
    metrics: list[HospitalMetric] = []


# ---- training rounds -----------------------------------------------------
class RoundCreate(BaseModel):
    num_rounds: int = Field(ge=1, le=100, default=5)
    local_epochs: int = Field(ge=1, le=20, default=2)
    dp_enabled: bool = False
    dp_epsilon: float = Field(gt=0, le=100, default=8.0)
    secure_aggregation: bool = False
    hospital_ids: list[int] = Field(min_length=1)


class RoundHistoryPoint(BaseModel):
    round_number: int
    accuracy: float
    auc: float
    loss: float


class RoundOut(ORMModel):
    id: int
    status: str
    num_rounds: int
    local_epochs: int
    dp_enabled: bool
    dp_epsilon: float
    secure_aggregation: bool
    hospital_ids: list[int]
    current_round: int
    global_accuracy: float | None
    global_auc: float | None
    global_loss: float | None
    error: str | None
    created_at: datetime
    completed_at: datetime | None


class ClientUpdateOut(ORMModel):
    id: int
    hospital_id: int
    hospital_name: str = ""
    round_number: int
    num_samples: int
    local_loss: float
    local_accuracy: float
    update_norm: float
    created_at: datetime


class RoundDetail(RoundOut):
    history: list[RoundHistoryPoint] = []
    updates: list[ClientUpdateOut] = []


# ---- models --------------------------------------------------------------
class ModelVersionOut(ORMModel):
    id: int
    version: str
    round_id: int | None
    accuracy: float
    auc: float
    loss: float
    num_parameters: int
    is_active: bool
    created_at: datetime


# ---- predictions ---------------------------------------------------------
class PredictionInput(BaseModel):
    age: float = Field(ge=18, le=110)
    sex: int = Field(ge=0, le=1)
    systolic_bp: float = Field(ge=60, le=260)
    diastolic_bp: float = Field(ge=30, le=160)
    cholesterol: float = Field(ge=80, le=500)
    hdl: float = Field(ge=10, le=150)
    bmi: float = Field(ge=10, le=80)
    glucose: float = Field(ge=40, le=500)
    smoker: int = Field(ge=0, le=1)
    family_history: int = Field(ge=0, le=1)


class PredictionOut(ORMModel):
    id: int
    probability: float
    diagnosis: str
    risk_level: str
    model_version: str = ""
    features: dict = {}
    created_at: datetime


# ---- audit / stats -------------------------------------------------------
class AuditEventOut(ORMModel):
    id: int
    actor_email: str
    action: str
    resource: str
    detail: str
    created_at: datetime


class StatsOverview(BaseModel):
    hospitals: int
    hospitals_online: int
    rounds_completed: int
    active_model_accuracy: float | None
    active_model_auc: float | None
    predictions_made: int
    last_round: RoundOut | None
