# federated-health-ai

A federated learning platform that lets hospitals collaboratively train a
cardiovascular-risk diagnosis model **without any patient data leaving the
hospital**. The aggregation server only ever sees model parameter updates —
optionally clipped, noised (differential privacy) and masked (secure
aggregation) — never raw records.

## Features

- **Federated training engine** — FedAvg with sample weighting, FedProx
  proximal term for non-IID stability, server learning rate, warm-start from
  checkpoints; deterministic and fully covered by tests.
- **Differential privacy** — per-client L2 clipping + Gaussian mechanism
  calibrated to (ε, δ); configurable per training job from the UI.
- **Secure aggregation** — pairwise additive masking (Bonawitz-style), so the
  server can only recover the *sum* of client updates.
- **Two execution modes** — an in-process simulation engine that powers the
  API/UI, and a real distributed deployment using Flower + PyTorch clients
  (`docker compose --profile flower up`). The numerical core is shared: the
  NumPy reference model and the PyTorch mirror are parameter-compatible and
  parity-tested.
- **Full platform** — JWT auth with roles, hospital registry, live training
  rounds over WebSocket, model registry with activation, clinical risk
  prediction console, append-only audit log, dashboard stats.
- **React frontend** — 14 screens (dashboard, hospitals, rounds with live
  charts, model registry, prediction console, audit, …), zustand state,
  typed API client, vitest suite.

## Quickstart (local)

```bash
# Backend (Python 3.11+)
pip install -r backend/requirements-dev.txt
python scripts/seed.py                       # demo admin + hospitals + a trained model
uvicorn app.main:app --app-dir backend --reload   # http://localhost:8000/api/docs

# Frontend
cd frontend && npm install && npm run dev    # http://localhost:5173
```

Demo login: `admin@federated.health` / `admin12345`.

## Quickstart (Docker)

```bash
docker compose up --build            # Postgres + API (migrated & seeded) + web UI
# UI: http://localhost:5173   API docs: http://localhost:8000/api/docs

docker compose --profile flower up   # real Flower server + 3 hospital clients
```

## Tests

```bash
python -m pytest --cov               # 74 tests, ~97% line coverage
cd frontend && npx vitest run        # 26 tests
```

## Layout

```
fl_core/       federated learning engine (data, model, aggregation, privacy,
               simulation, Flower client/server, PyTorch mirror)
backend/       FastAPI app: auth, hospitals, rounds, models, predictions,
               audit, stats, WebSocket streaming; SQLAlchemy + Alembic
frontend/      React + TypeScript UI (Vite, zustand, recharts)
scripts/       seed data
docs/          API reference, FYP report outline
tests/         fl_core test suite (backend tests live in backend/tests)
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for design details and
[docs/API.md](docs/API.md) for the endpoint reference.

## A note on data

Real patient records cannot ship with a repository, so hospitals hold
deterministic, clinically-plausible synthetic cohorts (Framingham-style risk
factors, per-hospital covariate shift, Dirichlet label skew). Every privacy
mechanism treats these shards exactly as it would treat real data.
