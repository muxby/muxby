"""Shared fixtures: each test gets a fresh in-memory database."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

import app.db.session as db_session
from app.db.session import Base, make_engine


@pytest.fixture()
def client(monkeypatch) -> TestClient:
    engine = make_engine("sqlite://")
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    monkeypatch.setattr(db_session, "engine", engine)
    monkeypatch.setattr(db_session, "SessionLocal", factory)
    # main.py captured SessionLocal by reference at import; routes look it up
    # through the module attribute, so patching the module is sufficient.
    from app.main import create_app

    test_app = create_app()
    with TestClient(test_app) as c:
        yield c


@pytest.fixture()
def auth_headers(client: TestClient) -> dict[str, str]:
    client.post(
        "/api/auth/register",
        json={"email": "doc@hospital.org", "password": "secret123", "full_name": "Dr. Grey"},
    )
    token = client.post(
        "/api/auth/login", data={"username": "doc@hospital.org", "password": "secret123"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def hospital_id(client: TestClient, auth_headers) -> int:
    resp = client.post(
        "/api/hospitals",
        json={"name": "St. Mary General", "region": "North", "data_size": 300},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def wait_for_round(client: TestClient, headers, round_id: int, timeout_s: float = 60.0) -> dict:
    """Poll until the round reaches a terminal state."""
    import time

    deadline = time.time() + timeout_s
    while time.time() < deadline:
        state = client.get(f"/api/rounds/{round_id}", headers=headers).json()
        if state["status"] in ("completed", "failed", "cancelled"):
            return state
        time.sleep(0.25)
    raise TimeoutError(f"round {round_id} did not finish within {timeout_s}s")
