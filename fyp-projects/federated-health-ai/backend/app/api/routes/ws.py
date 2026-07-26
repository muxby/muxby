"""Live round progress over WebSocket.

The training worker persists progress to the database as it happens; this
endpoint tails those tables and pushes deltas as JSON events. DB-tailing
(rather than in-process pub/sub) keeps the contract identical whether the
round runs in this process, another worker, or a real Flower deployment.
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import select

import app.db.session as db_session
from app.core.security import decode_access_token
from app.models import Hospital, TrainingRound

router = APIRouter(tags=["ws"])

TERMINAL = ("completed", "failed", "cancelled")
POLL_SECONDS = 0.5


@router.websocket("/ws/rounds/{round_id}")
async def round_events(websocket: WebSocket, round_id: int, token: str = Query(default="")):
    if decode_access_token(token) is None:
        await websocket.close(code=4401, reason="invalid token")
        return
    await websocket.accept()

    sent_history = 0
    sent_updates = 0
    last_status: str | None = None
    try:
        while True:
            snapshot = _snapshot(round_id, sent_history, sent_updates)
            if snapshot is None:
                await websocket.send_json({"type": "error", "detail": "round not found"})
                break
            status, history_events, update_events, total_rounds = snapshot

            for event in update_events:
                await websocket.send_json(event)
            sent_updates += len(update_events)

            for event in history_events:
                event["total_rounds"] = total_rounds
                await websocket.send_json(event)
            sent_history += len(history_events)

            if status != last_status:
                await websocket.send_json({"type": "status", "status": status})
                last_status = status
            if status in TERMINAL:
                break
            await asyncio.sleep(POLL_SECONDS)
    except WebSocketDisconnect:
        return
    await websocket.close()


def _snapshot(round_id: int, skip_history: int, skip_updates: int):
    """Read new events for the round in a short-lived session (thread-safe)."""
    db = db_session.SessionLocal()
    try:
        rnd = db.get(TrainingRound, round_id)
        if rnd is None:
            return None
        names = {h.id: h.name for h in db.scalars(select(Hospital))}
        history_events = [
            {
                "type": "round_progress",
                "round_number": h["round_number"],
                "accuracy": h["accuracy"],
                "auc": h["auc"],
                "loss": h["loss"],
            }
            for h in rnd.history[skip_history:]
        ]
        updates = sorted(rnd.updates, key=lambda u: u.id)[skip_updates:]
        update_events = [
            {
                "type": "client_update",
                "hospital_name": names.get(u.hospital_id, f"hospital-{u.hospital_id}"),
                "round_number": u.round_number,
                "local_accuracy": u.local_accuracy,
                "local_loss": u.local_loss,
            }
            for u in updates
        ]
        return rnd.status, history_events, update_events, rnd.num_rounds
    finally:
        db.close()
