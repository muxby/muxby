# Architecture

## System overview

```
┌────────────┐   REST/WS    ┌──────────────────┐    thread    ┌─────────────────────┐
│  React UI  │ ───────────► │  FastAPI backend │ ───────────► │  FederatedSimulation │
│ (14 pages) │              │  auth · registry │              │  fl_core engine      │
└────────────┘              │  rounds · audit  │ ◄─────────── │  (per-round progress │
                            └───────┬──────────┘   DB writes  │   persisted live)    │
                                    │                          └─────────────────────┘
                             SQLAlchemy / Alembic
                                    │
                              Postgres / SQLite
                                                        ┌────────────────────────────┐
     docker compose --profile flower                    │ Flower server + N clients  │
     (real distributed mode, same numerical core) ────► │ TorchMLP, FedAvg strategy  │
                                                        └────────────────────────────┘
```

## fl_core — the federated engine

Everything numerical operates on `list[np.ndarray]` (Flower's `NDArrays`
convention), which is what makes one aggregation/privacy implementation serve
both execution modes.

| Module | Responsibility |
|---|---|
| `data.py` | Synthetic cardio cohort generator (deterministic, per-hospital `risk_shift` covariate shift), `FeatureScaler`, Dirichlet non-IID partitioning |
| `nn.py` | Reference MLP (10→64→32→1) with manual backprop + Adam — no framework dependency, numerically verified against finite differences |
| `trainer.py` | Local training loop with optional FedProx proximal term; evaluation (loss/accuracy/AUC) |
| `aggregation.py` | Sample-weighted FedAvg over updates or deltas, server learning rate |
| `privacy.py` | L2 clipping, Gaussian mechanism σ(ε, δ, S), pairwise-mask secure aggregation |
| `simulation.py` | Orchestrates rounds: local train → delta → clip/noise → mask → aggregate → evaluate; progress callbacks + cancellation |
| `torch_model.py` | Parameter-compatible PyTorch mirror (parity-tested) |
| `flower_client.py` / `flower_server.py` | Real distributed deployment |

### Privacy design

- **DP-FedAvg**: each client's *delta* is clipped to `C`, then
  `N(0, σ²)` noise with `σ = √(2 ln(1.25/δ)) · C / ε` is added — the Gaussian
  mechanism, giving per-round (ε, δ)-DP w.r.t. one client's contribution.
- **Secure aggregation**: every client pair (i, j) derives a mask from a
  shared per-round seed; i adds it, j subtracts it. Individual updates are
  uniformly-masked noise to the server; the sum is exact. When enabled,
  clients pre-weight deltas by sample share so the server never needs
  per-client weights. A test asserts masked aggregation is bit-for-bit
  equal (atol 1e-8) to plain FedAvg.
- **Scaler**: feature standardisation is fitted on a *public reference
  cohort*, never on hospital shards, so no per-hospital statistics leak.

## Backend

- **Layered**: routes → services → ORM. Routes translate service exceptions
  to HTTP codes; services own transactions and write the audit trail.
- **Training jobs** run in a worker thread with its own session. Progress
  (per-round history, per-client updates) is *persisted as it happens*;
  the WebSocket endpoint tails the DB and pushes deltas. This keeps the
  streaming contract identical regardless of where training actually runs,
  and makes cancellation a simple status flip the worker polls.
- **Model registry** stores weights + scaler as compressed npz blobs; the
  best model by AUC auto-activates, and any version can be activated
  manually. Predictions always record which version served them.
- **Auth**: bcrypt password hashing, HS256 JWTs, OAuth2 password flow;
  first registered user becomes admin.
- **Migrations**: Alembic (`backend/alembic`); `create_all` additionally
  runs at startup so a fresh SQLite checkout works with zero setup.

## Frontend

Vite + React 18 + TypeScript. `zustand` for auth/toast state, typed fetch
client with automatic Bearer injection and 401 auto-logout, `useRoundSocket`
hook for live round streaming with a 4-second polling fallback, recharts for
metric visualisation. All 14 screens handle loading/error/empty states.

## Testing strategy

- `tests/fl_core` — unit tests of every numerical property worth trusting:
  gradient correctness vs finite differences, mask cancellation, DP noise
  calibration, determinism, non-IID partition coverage, torch parity.
- `backend/tests` — API integration tests on an isolated in-memory DB per
  test: auth flows, CRUD validation, a *real* federated round through the
  HTTP API (including DP + secure aggregation), WebSocket streaming to
  completion, audit/stats lifecycle.
- Coverage: ~97% lines across `fl_core` + `backend/app` (CI enforces ≥80%).

## Deployment

`docker-compose.yml` runs Postgres, the API (migrate → seed → serve) and the
nginx-served UI. The optional `flower` profile starts a Flower aggregation
server and three PyTorch hospital clients sharing the same model definition
as the simulation engine.
