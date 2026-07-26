# API Reference

Base URL: `/api`. Interactive docs (Swagger UI) at `/api/docs`.

Authentication: `Authorization: Bearer <JWT>` on every endpoint except
`/auth/register`, `/auth/login`, `/health`. Obtain a token via the OAuth2
password flow.

## Auth

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/auth/register` | `{email, password (≥8), full_name}` | `201` User — first user gets role `admin` |
| POST | `/auth/login` | form: `username`, `password` | `{access_token, token_type}` |
| GET | `/auth/me` | — | current User |

Errors: `409` duplicate email, `401` bad credentials, `422` validation.

## Hospitals

| Method | Path | Notes |
|---|---|---|
| GET | `/hospitals` | list all |
| POST | `/hospitals` | `{name, region, data_size (50–100000), risk_shift (−2..2)}` → `201`; `409` on duplicate name |
| GET | `/hospitals/{id}` | includes `metrics[]`: per-round local `{round_id, accuracy, auc, loss}` |
| PATCH | `/hospitals/{id}` | partial: `name`, `region`, `data_size`, `status ∈ {online, offline}` |
| DELETE | `/hospitals/{id}` | `204` |

## Training rounds

| Method | Path | Notes |
|---|---|---|
| GET | `/rounds` | newest first |
| POST | `/rounds` | `{num_rounds (1–100), local_epochs (1–20), dp_enabled, dp_epsilon (0–100], secure_aggregation, hospital_ids[]}` → `201`, job starts immediately; `400` if a hospital is unknown or offline |
| GET | `/rounds/{id}` | adds `history[]` (`{round_number, accuracy, auc, loss}`) and `updates[]` (per-hospital `{hospital_name, round_number, num_samples, local_loss, local_accuracy, update_norm}`) |
| POST | `/rounds/{id}/cancel` | stops between FL rounds |

Round `status`: `pending → running → completed | failed | cancelled`.

## Models

| Method | Path | Notes |
|---|---|---|
| GET | `/models` | registry, newest first |
| GET | `/models/{id}` | one version |
| POST | `/models/{id}/activate` | make this version serve predictions (exactly one active) |

Versions are created automatically when a round completes; the best AUC
auto-activates.

## Predictions

| Method | Path | Notes |
|---|---|---|
| POST | `/predictions` | clinical features (below) → `{probability, diagnosis, risk_level, model_version}`; `409` when no active model |
| GET | `/predictions` | caller's history, features echoed |

Features: `age` 18–110, `sex` 0/1, `systolic_bp` 60–260, `diastolic_bp`
30–160, `cholesterol` 80–500, `hdl` 10–150, `bmi` 10–80, `glucose` 40–500,
`smoker` 0/1, `family_history` 0/1. `risk_level`: `<0.33` low,
`<0.66` moderate, else high.

## Audit & stats

| Method | Path | Notes |
|---|---|---|
| GET | `/audit?limit=100` | append-only trail: `{actor_email, action, resource, detail, created_at}` |
| GET | `/stats/overview` | dashboard aggregates incl. `last_round` |
| GET | `/health` | unauthenticated liveness |

## WebSocket

`GET /api/ws/rounds/{id}?token=<JWT>` — streams JSON events until the round
reaches a terminal status:

```jsonc
{"type": "status", "status": "running"}
{"type": "client_update", "hospital_name": "St. Mary General",
 "round_number": 1, "local_accuracy": 0.71, "local_loss": 0.60}
{"type": "round_progress", "round_number": 1, "total_rounds": 5,
 "accuracy": 0.74, "auc": 0.77, "loss": 0.55}
{"type": "status", "status": "completed"}
```

Invalid tokens are closed with code `4401`; unknown rounds receive
`{"type": "error"}`.
