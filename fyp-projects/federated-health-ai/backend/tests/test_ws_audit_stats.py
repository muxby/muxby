"""WebSocket streaming, audit log, and dashboard stats."""

import pytest

from tests.conftest import wait_for_round


def _token(auth_headers: dict) -> str:
    return auth_headers["Authorization"].split(" ", 1)[1]


def test_ws_rejects_bad_token(client, auth_headers, hospital_id):
    r = client.post(
        "/api/rounds",
        json={"num_rounds": 1, "local_epochs": 1, "hospital_ids": [hospital_id]},
        headers=auth_headers,
    )
    rid = r.json()["id"]
    # Server closes with 4401 before accepting; the test client surfaces
    # that as a WebSocketDisconnect either at connect or on first receive.
    from starlette.websockets import WebSocketDisconnect

    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(f"/api/ws/rounds/{rid}?token=bogus") as ws:
            ws.receive_json()


def test_ws_streams_round_to_completion(client, auth_headers, hospital_id):
    r = client.post(
        "/api/rounds",
        json={"num_rounds": 2, "local_epochs": 1, "hospital_ids": [hospital_id]},
        headers=auth_headers,
    )
    rid = r.json()["id"]
    events = []
    with client.websocket_connect(f"/api/ws/rounds/{rid}?token={_token(auth_headers)}") as ws:
        while True:
            event = ws.receive_json()
            events.append(event)
            if event.get("type") == "status" and event.get("status") in (
                "completed", "failed", "cancelled",
            ):
                break
    kinds = {e["type"] for e in events}
    assert "status" in kinds
    assert "round_progress" in kinds
    assert "client_update" in kinds
    progress = [e for e in events if e["type"] == "round_progress"]
    assert [p["round_number"] for p in progress] == [1, 2]
    assert all(p["total_rounds"] == 2 for p in progress)
    final = [e for e in events if e["type"] == "status"][-1]
    assert final["status"] == "completed"


def test_ws_unknown_round_sends_error(client, auth_headers):
    with client.websocket_connect(f"/api/ws/rounds/424242?token={_token(auth_headers)}") as ws:
        assert ws.receive_json()["type"] == "error"


def test_audit_trail_records_actions(client, auth_headers, hospital_id):
    events = client.get("/api/audit", headers=auth_headers).json()
    actions = [e["action"] for e in events]
    assert "user.register" in actions
    assert "hospital.create" in actions
    assert all(e["actor_email"] for e in events)


def test_audit_limit_param(client, auth_headers, hospital_id):
    events = client.get("/api/audit?limit=1", headers=auth_headers).json()
    assert len(events) == 1


def test_stats_overview_lifecycle(client, auth_headers, hospital_id):
    before = client.get("/api/stats/overview", headers=auth_headers).json()
    assert before["hospitals"] == 1
    assert before["rounds_completed"] == 0
    assert before["active_model_accuracy"] is None
    assert before["last_round"] is None

    r = client.post(
        "/api/rounds",
        json={"num_rounds": 1, "local_epochs": 1, "hospital_ids": [hospital_id]},
        headers=auth_headers,
    )
    wait_for_round(client, auth_headers, r.json()["id"])

    after = client.get("/api/stats/overview", headers=auth_headers).json()
    assert after["rounds_completed"] == 1
    assert after["active_model_accuracy"] is not None
    assert after["last_round"]["status"] == "completed"
