"""Integration tests: full federated round -> model registry -> prediction."""

import pytest

from tests.conftest import wait_for_round

FEATURES = {
    "age": 61, "sex": 1, "systolic_bp": 150, "diastolic_bp": 95,
    "cholesterol": 260, "hdl": 38, "bmi": 31, "glucose": 140,
    "smoker": 1, "family_history": 1,
}


@pytest.fixture()
def two_hospitals(client, auth_headers):
    ids = []
    for name in ("Alpha Med", "Beta Clinic"):
        r = client.post(
            "/api/hospitals",
            json={"name": name, "region": "Central", "data_size": 200},
            headers=auth_headers,
        )
        ids.append(r.json()["id"])
    return ids


def _run_round(client, headers, hospital_ids, **overrides):
    payload = {"num_rounds": 2, "local_epochs": 1, "hospital_ids": hospital_ids, **overrides}
    r = client.post("/api/rounds", json=payload, headers=headers)
    assert r.status_code == 201, r.text
    return wait_for_round(client, headers, r.json()["id"])


def test_full_round_produces_model_and_metrics(client, auth_headers, two_hospitals):
    state = _run_round(client, auth_headers, two_hospitals)
    assert state["status"] == "completed", state.get("error")
    assert state["global_auc"] is not None and 0.4 < state["global_auc"] <= 1.0
    assert len(state["history"]) == 2
    # 2 hospitals x 2 rounds of client updates, each naming its hospital
    assert len(state["updates"]) == 4
    assert {u["hospital_name"] for u in state["updates"]} == {"Alpha Med", "Beta Clinic"}

    models = client.get("/api/models", headers=auth_headers).json()
    assert len(models) == 1
    assert models[0]["is_active"] is True
    assert models[0]["num_parameters"] > 0


def test_round_with_dp_and_secure_aggregation(client, auth_headers, two_hospitals):
    state = _run_round(
        client, auth_headers, two_hospitals,
        dp_enabled=True, dp_epsilon=50.0, secure_aggregation=True,
    )
    assert state["status"] == "completed", state.get("error")
    assert state["dp_enabled"] is True
    assert state["secure_aggregation"] is True


def test_round_rejects_unknown_and_offline_hospitals(client, auth_headers, two_hospitals):
    r = client.post(
        "/api/rounds",
        json={"num_rounds": 1, "local_epochs": 1, "hospital_ids": [9999]},
        headers=auth_headers,
    )
    assert r.status_code == 400

    client.patch(
        f"/api/hospitals/{two_hospitals[0]}", json={"status": "offline"}, headers=auth_headers
    )
    r = client.post(
        "/api/rounds",
        json={"num_rounds": 1, "local_epochs": 1, "hospital_ids": two_hospitals},
        headers=auth_headers,
    )
    assert r.status_code == 400


def test_cancel_pending_round(client, auth_headers, two_hospitals):
    r = client.post(
        "/api/rounds",
        json={"num_rounds": 50, "local_epochs": 5, "hospital_ids": two_hospitals},
        headers=auth_headers,
    )
    rid = r.json()["id"]
    cancel = client.post(f"/api/rounds/{rid}/cancel", headers=auth_headers)
    assert cancel.status_code == 200
    state = wait_for_round(client, auth_headers, rid)
    assert state["status"] == "cancelled"


def test_model_activation_switch(client, auth_headers, two_hospitals):
    _run_round(client, auth_headers, two_hospitals)
    _run_round(client, auth_headers, two_hospitals, num_rounds=1)
    models = client.get("/api/models", headers=auth_headers).json()
    assert len(models) == 2
    inactive = next(m for m in models if not m["is_active"])
    r = client.post(f"/api/models/{inactive['id']}/activate", headers=auth_headers)
    assert r.status_code == 200 and r.json()["is_active"] is True
    models = client.get("/api/models", headers=auth_headers).json()
    assert sum(m["is_active"] for m in models) == 1
    assert client.post("/api/models/999/activate", headers=auth_headers).status_code == 404


def test_prediction_requires_model_then_works(client, auth_headers, two_hospitals):
    r = client.post("/api/predictions", json=FEATURES, headers=auth_headers)
    assert r.status_code == 409  # no trained model yet

    _run_round(client, auth_headers, two_hospitals)
    r = client.post("/api/predictions", json=FEATURES, headers=auth_headers)
    assert r.status_code == 201
    body = r.json()
    assert 0.0 < body["probability"] < 1.0
    assert body["risk_level"] in ("low", "moderate", "high")
    assert body["diagnosis"] in ("high_risk", "low_risk")
    assert body["model_version"] == "v1.0"

    history = client.get("/api/predictions", headers=auth_headers).json()
    assert len(history) == 1
    assert history[0]["features"]["age"] == 61


def test_prediction_input_validation(client, auth_headers):
    bad = dict(FEATURES, age=300)
    assert client.post("/api/predictions", json=bad, headers=auth_headers).status_code == 422


def test_hospital_metrics_populated_after_round(client, auth_headers, two_hospitals):
    _run_round(client, auth_headers, two_hospitals)
    detail = client.get(f"/api/hospitals/{two_hospitals[0]}", headers=auth_headers).json()
    assert len(detail["metrics"]) == 1
    assert 0.0 <= detail["metrics"][0]["accuracy"] <= 1.0
