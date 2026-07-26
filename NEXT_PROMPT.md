# Next Session Instructions

Read `/home/user/muxby/PROGRESS.md` first (especially "Environment notes").
You are on branch `claude/fyp-projects-build-saz3hy` of muxby/muxby. Project 1
(`fyp-projects/federated-health-ai`) is COMPLETE — do not rework it unless its
tests fail.

## Goal: build project 2 — `fyp-projects/blockchain-supplychain` — to completion

A supply-chain provenance tracker with smart contracts. Stack: Solidity,
Hardhat, Node backend (ethers.js), Next.js frontend.

### Order of work
1. `npx hardhat init` style scaffold in `fyp-projects/blockchain-supplychain/chain/`
   (if the proxy blocks hardhat downloads, fall back to a hand-written minimal
   hardhat setup: package.json with hardhat + @nomicfoundation/hardhat-toolbox,
   hardhat.config.js). Contracts in `chain/contracts/`:
   - `SupplyChainRegistry.sol`: participant registration (producer, processor,
     carrier, retailer, auditor roles), role-gated modifiers, admin transfer.
   - `ProvenanceTracker.sol`: product batches (id, sku, origin, metadata URI,
     doc hash), lifecycle state machine (Created→Processed→InTransit→Received→
     Retail, plus Recalled from any state by auditor), custody transfer with
     accept/reject, per-batch event history, certification hash anchoring.
   Full NatSpec, events on every mutation, custom errors.
2. `chain/test/*.test.js` — full lifecycle, role enforcement, invalid
   transitions revert, recall, event assertions. `npx hardhat test` green.
3. `backend/` (Node + Express + ethers v6): JWT auth, routes for participants/
   batches/transfers/verify (hash file → compare on-chain), an event indexer
   writing to SQLite (better-sqlite3) for fast queries, service layer, jest or
   node:test suite using an in-process hardhat network. All tests green.
4. `frontend/` (Next.js app router): 10+ real screens — dashboard, batch list,
   batch detail with provenance timeline, create batch, transfer custody,
   participants admin, verify document, recalls, login, settings. Typed API
   client, tests for utils/components with vitest. `npm run build` green.
5. `docker-compose.yml` (hardhat node, deployer/seeder, api, web), root CI
   workflow: append jobs to `.github/workflows/ci.yml` (keep existing
   federated-health-ai jobs intact). `scripts/seed.js` deploys contracts and
   creates demo participants + batches.
6. Docs: README.md, ARCHITECTURE.md, docs/API.md, docs/FYP_REPORT_OUTLINE.md.
7. Run ALL project 2 test suites; fix until green.
8. Update `/home/user/muxby/PROGRESS.md` (mark project 2 complete, write exact
   next 5 tasks for project 3 realtime-fraud-engine) and rewrite this file
   (`NEXT_PROMPT.md`) with self-contained instructions for project 3.
9. Commit (small logical commits or one per project) and push:
   `git push -u origin claude/fyp-projects-build-saz3hy` (retry w/ backoff on
   network errors only).

### Rules carried forward
- No placeholder implementations (`pass`, `// TODO`) — implement everything.
- Files > 500 lines must be split.
- Print a progress table at the end of the session; end the final message with
  `STATUS: CONTINUE` (only `STATUS: ALL_COMPLETE` when all 10 projects pass).
- If tests fail at session end, fixing them is the top task in this file.

### Verify project 1 still green (fast check, optional)
```
cd /home/user/muxby/fyp-projects/federated-health-ai && python3 -m pytest -q
```
