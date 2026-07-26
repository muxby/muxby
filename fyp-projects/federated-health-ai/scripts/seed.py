"""Seed the database with a demo admin, hospitals, and one completed round.

Run from the project root (or the backend container):

    python scripts/seed.py
"""

from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "backend")]

from app.db.session import Base, SessionLocal, engine  # noqa: E402
from app.schemas.api import HospitalCreate, RoundCreate  # noqa: E402
from app.services import auth_service, hospital_service, training_service  # noqa: E402
from app.services.auth_service import EmailAlreadyRegistered  # noqa: E402

DEMO_EMAIL = "admin@federated.health"
DEMO_PASSWORD = "admin12345"

HOSPITALS = [
    ("St. Mary General", "North", 1200, 0.0),
    ("Riverside Medical Center", "South", 800, 0.4),
    ("Hillcrest University Hospital", "East", 1500, -0.3),
]


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        try:
            user = auth_service.register_user(db, DEMO_EMAIL, DEMO_PASSWORD, "Platform Admin")
            print(f"created admin {DEMO_EMAIL} / {DEMO_PASSWORD}")
        except EmailAlreadyRegistered:
            user = auth_service.get_user_by_email(db, DEMO_EMAIL)
            print("admin already exists — reusing")
        assert user is not None

        existing = {h.name for h in hospital_service.list_hospitals(db)}
        hospital_ids = []
        for name, region, size, shift in HOSPITALS:
            if name in existing:
                hospital_ids.append(
                    next(h.id for h in hospital_service.list_hospitals(db) if h.name == name)
                )
                continue
            hospital = hospital_service.create_hospital(
                db,
                HospitalCreate(name=name, region=region, data_size=size, risk_shift=shift),
                actor_email=DEMO_EMAIL,
            )
            hospital_ids.append(hospital.id)
            print(f"created hospital {name} (id={hospital.id})")

        if not any(r.status == "completed" for r in training_service.list_rounds(db)):
            rnd = training_service.create_round(
                db,
                RoundCreate(num_rounds=5, local_epochs=2, hospital_ids=hospital_ids),
                actor_email=DEMO_EMAIL,
                user_id=user.id,
            )
            print(f"running seed training round {rnd.id} (5 rounds x 3 hospitals)...")
            training_service.execute_round(rnd.id, SessionLocal)
            rnd = training_service.get_round(db, rnd.id)
            db.refresh(rnd)
            print(f"round {rnd.id} finished: {rnd.status}, AUC={rnd.global_auc:.3f}")
        else:
            print("completed round already present — skipping training")
    finally:
        db.close()
    print("seed complete")


if __name__ == "__main__":
    main()
