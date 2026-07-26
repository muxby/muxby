"""In-process federated training engine.

Drives the same client/server round structure as the Flower deployment but
inside one process, which is what the API server uses to run training rounds
it can stream over WebSockets. Each simulated hospital only ever touches its
own data shard; the "server" only sees (optionally clipped, noised, masked)
parameter deltas — the trust boundaries of the real deployment are preserved
in code structure even though everything shares a process.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from fl_core.aggregation import apply_delta, fedavg, update_norm
from fl_core.data import NUM_FEATURES
from fl_core.nn import MLP
from fl_core.privacy import SecureAggregator, apply_dp
from fl_core.trainer import EvalResult, evaluate, train_local

NDArrays = list[np.ndarray]
ProgressCallback = Callable[[dict], None]


@dataclass
class RoundConfig:
    num_rounds: int = 5
    local_epochs: int = 2
    batch_size: int = 32
    lr: float = 1e-3
    prox_mu: float = 0.0
    server_lr: float = 1.0
    dp_enabled: bool = False
    dp_epsilon: float = 8.0
    dp_delta: float = 1e-5
    dp_clip_norm: float = 5.0
    secure_aggregation: bool = False
    seed: int = 0

    def validate(self) -> None:
        if self.num_rounds < 1:
            raise ValueError("num_rounds must be >= 1")
        if self.local_epochs < 1:
            raise ValueError("local_epochs must be >= 1")
        if self.dp_enabled and self.dp_epsilon <= 0:
            raise ValueError("dp_epsilon must be positive when DP is enabled")


@dataclass
class ClientUpdateRecord:
    client_id: int
    round_number: int
    num_samples: int
    local_loss: float
    local_accuracy: float
    local_auc: float
    update_norm: float


@dataclass
class RoundHistoryEntry:
    round_number: int
    loss: float
    accuracy: float
    auc: float


@dataclass
class SimulationResult:
    history: list[RoundHistoryEntry] = field(default_factory=list)
    client_updates: list[ClientUpdateRecord] = field(default_factory=list)
    final_params: NDArrays = field(default_factory=list)
    final_eval: EvalResult | None = None
    cancelled: bool = False


class FederatedSimulation:
    """One federated training job over a fixed set of client shards.

    ``client_datasets`` maps client id -> (X, y) with features already
    standardised. ``progress_cb`` receives JSON-serialisable event dicts;
    ``cancel_cb`` is polled between rounds.
    """

    def __init__(
        self,
        client_datasets: dict[int, tuple[np.ndarray, np.ndarray]],
        test_set: tuple[np.ndarray, np.ndarray],
        config: RoundConfig,
        initial_params: NDArrays | None = None,
        progress_cb: ProgressCallback | None = None,
        cancel_cb: Callable[[], bool] | None = None,
    ):
        if not client_datasets:
            raise ValueError("at least one client dataset is required")
        config.validate()
        self.client_datasets = client_datasets
        self.test_set = test_set
        self.config = config
        self.progress_cb = progress_cb or (lambda event: None)
        self.cancel_cb = cancel_cb or (lambda: False)
        self.model = MLP(NUM_FEATURES, seed=config.seed)
        if initial_params is not None:
            self.model.set_parameters(initial_params)

    def run(self) -> SimulationResult:
        result = SimulationResult()
        cfg = self.config
        global_params = self.model.get_parameters()
        rng = np.random.default_rng(cfg.seed)

        for round_number in range(1, cfg.num_rounds + 1):
            if self.cancel_cb():
                result.cancelled = True
                break
            round_updates = self._run_clients(global_params, round_number, rng, result)
            agg_delta = self._aggregate(round_updates)
            global_params = apply_delta(global_params, agg_delta, cfg.server_lr)
            self.model.set_parameters(global_params)

            ev = evaluate(self.model, *self.test_set)
            result.history.append(
                RoundHistoryEntry(round_number, ev.loss, ev.accuracy, ev.auc)
            )
            self.progress_cb(
                {
                    "type": "round_progress",
                    "round_number": round_number,
                    "total_rounds": cfg.num_rounds,
                    "accuracy": ev.accuracy,
                    "auc": ev.auc,
                    "loss": ev.loss,
                }
            )

        result.final_params = global_params
        result.final_eval = evaluate(self.model, *self.test_set)
        return result

    # ------------------------------------------------------------------
    def _run_clients(
        self,
        global_params: NDArrays,
        round_number: int,
        rng: np.random.Generator,
        result: SimulationResult,
    ) -> list[tuple[NDArrays, int]]:
        """Local training on every client; returns (delta, num_samples) pairs.

        With secure aggregation on, each client pre-weights its delta by its
        sample share and masks it — the server then only sums, never seeing
        an individual hospital's update.
        """
        cfg = self.config
        client_ids = sorted(self.client_datasets)
        total_samples = sum(len(self.client_datasets[c][0]) for c in client_ids)
        secagg = (
            SecureAggregator(client_ids, round_seed=cfg.seed * 100_003 + round_number)
            if cfg.secure_aggregation and len(client_ids) > 1
            else None
        )

        raw: list[tuple[NDArrays, int]] = []
        for client_id in client_ids:
            X, y = self.client_datasets[client_id]
            local = MLP(NUM_FEATURES, seed=cfg.seed)
            local.set_parameters(global_params)
            loss = train_local(
                local,
                X,
                y,
                epochs=cfg.local_epochs,
                batch_size=cfg.batch_size,
                lr=cfg.lr,
                prox_mu=cfg.prox_mu,
                seed=cfg.seed * 7 + round_number * 31 + client_id,
            )
            delta = [lp - gp for lp, gp in zip(local.get_parameters(), global_params)]
            norm = update_norm(delta)
            if cfg.dp_enabled:
                delta, norm = apply_dp(
                    delta,
                    epsilon=cfg.dp_epsilon,
                    dp_delta=cfg.dp_delta,
                    clip_norm=cfg.dp_clip_norm,
                    rng=rng,
                )
            ev = evaluate(local, X, y)
            record = ClientUpdateRecord(
                client_id=client_id,
                round_number=round_number,
                num_samples=len(X),
                local_loss=loss,
                local_accuracy=ev.accuracy,
                local_auc=ev.auc,
                update_norm=norm,
            )
            result.client_updates.append(record)
            self.progress_cb(
                {
                    "type": "client_update",
                    "client_id": client_id,
                    "round_number": round_number,
                    "num_samples": record.num_samples,
                    "local_accuracy": ev.accuracy,
                    "local_auc": ev.auc,
                    "local_loss": loss,
                    "update_norm": norm,
                }
            )
            raw.append((delta, len(X)))

        if secagg is None:
            return raw

        masked = [
            (secagg.mask(cid, [a * (n / total_samples) for a in delta]), n)
            for cid, (delta, n) in zip(client_ids, raw)
        ]
        summed = SecureAggregator.unmask_sum([m for m, _ in masked])
        # The sum of pre-weighted deltas IS the weighted average; return it
        # as a single pseudo-update so _aggregate is a no-op average.
        return [(summed, total_samples)]

    def _aggregate(self, updates: list[tuple[NDArrays, int]]) -> NDArrays:
        return fedavg(updates)
