# FYP Projects — Build Progress

## Status
- **Current project**: 1 of 10 — `federated-health-ai` — **COMPLETE** (all tests green)
- **Next project**: 2 of 10 — `blockchain-supplychain` — not started
- **Current module**: n/a (between projects)

## Project checklist

| # | Project | Status | Tests |
|---|---------|--------|-------|
| 1 | federated-health-ai | ✅ complete | 74 Python (97% cov) + 26 vitest, all passing |
| 2 | blockchain-supplychain | ⬜ not started | — |
| 3 | realtime-fraud-engine | ⬜ not started | — |
| 4 | autonomous-drone-sim | ⬜ not started | — |
| 5 | llm-legal-assistant | ⬜ not started | — |
| 6 | smart-grid-optimizer | ⬜ not started | — |
| 7 | deepfake-detector | ⬜ not started | — |
| 8 | distributed-code-judge | ⬜ not started | — |
| 9 | sign-language-translator | ⬜ not started | — |
| 10 | privacy-social-network | ⬜ not started | — |

## Project 1 summary (done this session)
- `fl_core/`: synthetic cardio cohort + Dirichlet non-IID partitioning; NumPy
  reference MLP with manual backprop (finite-difference verified) + Adam;
  FedAvg/FedProx; DP (clip + Gaussian mechanism); secure aggregation
  (pairwise masks, exactness-tested); in-process simulation engine with
  progress/cancel; PyTorch mirror (parity-tested); Flower client+server.
- `backend/`: FastAPI — JWT auth (bcrypt), hospitals CRUD, training rounds
  run in worker threads with live DB-persisted progress, WebSocket streaming,
  model registry (npz blobs, activation), prediction console, audit log,
  stats; SQLAlchemy + Alembic migration; seed script (trains a real model).
- `frontend/`: Vite+React+TS, 14 pages, zustand, recharts, WS live charts,
  26 vitest tests, `npm run build` clean.
- Docker: compose stack (Postgres+API+nginx UI) + optional `flower` profile
  (real distributed FL). CI: `.github/workflows/ci.yml` (pytest w/ cov-fail-under=80 + vitest/build).
- Docs: README, ARCHITECTURE, docs/API.md, docs/FYP_REPORT_OUTLINE.md.

## Environment notes (IMPORTANT for next session)
- `pip install` works from PyPI; download.pytorch.org is BLOCKED by proxy —
  plain `pip install torch` works (CUDA wheel).
- System `cryptography` deb package is broken → `pip install --ignore-installed cryptography cffi`.
- passlib is incompatible with bcrypt 5.x → project uses `bcrypt` directly.
- FastAPI 0.140 requires `starlette>=0.40,<0.51` (1.x got pulled in once — pin it).
- Frontend already has node_modules installed locally (not committed).

## Exact next 5 tasks (project 2: blockchain-supplychain)
1. Scaffold `fyp-projects/blockchain-supplychain/` — Hardhat project with
   Solidity contracts: `SupplyChainRegistry.sol` (participants, roles),
   `ProvenanceTracker.sol` (batch lifecycle: created→processed→shipped→
   received→retail, custody transfers, cert hashes), events for every
   transition. No placeholder functions.
2. Contract tests (Hardhat + chai) covering lifecycle, access control,
   double-transfer rejection, event emission — aim 90%+ of contract paths.
3. Node/Express (or Fastify) backend: ethers.js service layer against a
   local Hardhat node, REST API (auth via JWT, participants, batches,
   transfers, verification endpoint hashing off-chain docs), SQLite/Postgres
   mirror of on-chain state via event indexer, tests with in-process hardhat.
4. Next.js frontend: 10+ screens (dashboard, batches, batch timeline/QR,
   transfer flow, participants, verify document, audit), state via zustand
   or React Query, tests.
5. Docker compose (hardhat node + indexer + api + web), CI job, seed script
   (deploy + demo batches), README/ARCHITECTURE/API/FYP outline. Update
   PROGRESS.md + NEXT_PROMPT.md when done.

## Blockers
- None. (If npm registry or specific package installs fail via proxy, note it here.)
