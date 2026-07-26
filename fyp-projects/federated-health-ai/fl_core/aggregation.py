"""Server-side aggregation of client updates (FedAvg family)."""

from __future__ import annotations

import numpy as np

NDArrays = list[np.ndarray]


def fedavg(updates: list[tuple[NDArrays, int]]) -> NDArrays:
    """Sample-weighted average of client parameter lists.

    ``updates`` is ``[(params, num_samples), ...]``. Works equally on full
    parameter vectors or on deltas (new - global), which is how the
    simulation engine calls it so that clipping/DP compose correctly.
    """
    if not updates:
        raise ValueError("no updates to aggregate")
    total = sum(n for _, n in updates)
    if total <= 0:
        raise ValueError("total sample count must be positive")
    n_arrays = len(updates[0][0])
    for params, _ in updates:
        if len(params) != n_arrays:
            raise ValueError("inconsistent parameter list lengths across clients")
    agg: NDArrays = []
    for i in range(n_arrays):
        acc = np.zeros_like(updates[0][0][i], dtype=np.float64)
        for params, n in updates:
            acc += params[i] * (n / total)
        agg.append(acc)
    return agg


def apply_delta(global_params: NDArrays, delta: NDArrays, server_lr: float = 1.0) -> NDArrays:
    """Apply an aggregated delta to the global model with a server learning rate."""
    if len(global_params) != len(delta):
        raise ValueError("delta length mismatch")
    return [g + server_lr * d for g, d in zip(global_params, delta)]


def weighted_metric(values: list[tuple[float, int]]) -> float:
    """Sample-weighted mean of a scalar metric: ``[(value, num_samples), ...]``."""
    total = sum(n for _, n in values)
    if total <= 0:
        raise ValueError("total sample count must be positive")
    return float(sum(v * n for v, n in values) / total)


def update_norm(delta: NDArrays) -> float:
    """Global L2 norm across every array in an update."""
    return float(np.sqrt(sum(float(np.sum(a**2)) for a in delta)))
