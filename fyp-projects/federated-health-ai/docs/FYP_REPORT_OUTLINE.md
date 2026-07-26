# FYP Report Outline — Federated Learning for Privacy-Preserving Hospital Diagnosis

## 1. Introduction
- 1.1 Motivation: clinical ML is data-hungry; health data is siloed by law
  (HIPAA/GDPR) and by institutional risk aversion.
- 1.2 Problem statement: train a diagnostic model across hospitals such that
  no raw patient record, and ideally no individually-attributable update,
  leaves its origin.
- 1.3 Objectives: working FL platform; quantified privacy (ε, δ);
  utility within an acceptable margin of centralised training; usable
  operator tooling (live monitoring, model registry, audit).
- 1.4 Scope and assumptions (honest-but-curious server, no client dropout
  recovery, synthetic cohorts standing in for patient data).

## 2. Background & Related Work
- 2.1 Federated averaging (McMahan et al., 2017) and the FedProx extension
  for statistical heterogeneity (Li et al., 2020).
- 2.2 Differential privacy: the Gaussian mechanism, DP-FedAvg, per-round vs
  composed budgets.
- 2.3 Secure aggregation (Bonawitz et al., 2017).
- 2.4 FL frameworks (Flower, TFF, FedML) and why Flower was chosen.
- 2.5 Cardiovascular risk modelling (Framingham) as the clinical grounding.

## 3. System Design
- 3.1 Architecture: simulation engine vs distributed deployment; shared
  NDArrays numerical core (reference ARCHITECTURE.md diagram).
- 3.2 Threat model and where each mechanism cuts: clipping, Gaussian noise,
  pairwise masking, public-cohort scaler fitting.
- 3.3 Platform design: services layer, persisted-progress streaming, model
  registry with provenance, append-only audit.
- 3.4 Data design: synthetic cohort generator, covariate shift via
  risk_shift, Dirichlet label skew.

## 4. Implementation
- 4.1 fl_core: manual-backprop reference network and why (verifiability:
  finite-difference gradient tests); PyTorch mirror and parity testing.
- 4.2 Privacy mechanisms: clip → noise → mask pipeline; client-side
  pre-weighting under secure aggregation.
- 4.3 Backend: FastAPI, SQLAlchemy/Alembic, JWT auth, WebSocket tailing.
- 4.4 Frontend: typed API client, live round dashboards.
- 4.5 Deployment: docker-compose topologies (app stack; Flower profile).

## 5. Evaluation
- 5.1 Utility: federated vs centralised AUC/accuracy on held-out cohort;
  effect of non-IID α; FedProx ablation.
- 5.2 Privacy/utility trade-off: AUC vs ε sweep at fixed δ, clip norm
  sensitivity.
- 5.3 Overhead: secure aggregation exactness (masked ≡ plain aggregate) and
  runtime cost per round.
- 5.4 Robustness: cancellation, failure persistence, warm-start behaviour.
- 5.5 Test coverage summary (74 backend/core tests, 26 frontend tests,
  ~97% line coverage).

## 6. Discussion
- 6.1 Limitations: per-round (not composed) DP accounting; no dropout
  recovery in masking; synthetic data caveats; honest-but-curious server.
- 6.2 Ethical & regulatory positioning.

## 7. Future Work
- Rényi-DP accountant for tight composition across rounds; client dropout
  recovery (full Bonawitz protocol); cross-silo deployment hardening (mTLS,
  hospital-side attestation); real-dataset validation under IRB approval.

## 8. Conclusion

## Appendices
- A. API reference (docs/API.md)
- B. Reproducing experiments (`python -m pytest`, seed script, compose profiles)
- C. Hyperparameters and seeds
