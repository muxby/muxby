"""Differential privacy and secure aggregation for client updates.

DP follows the Gaussian mechanism on clipped client deltas (DP-FedAvg):
each client's update is clipped to an L2 bound, then Gaussian noise scaled
to that bound is added, giving per-round (epsilon, delta)-DP with respect
to a single client's contribution.

Secure aggregation implements pairwise additive masking (Bonawitz et al.
2017, without the dropout-recovery protocol): every client pair derives a
shared seed, one adds a pseudo-random mask and the other subtracts it, so
individual updates are unreadable while their sum is exact.
"""

from __future__ import annotations

import hashlib

import numpy as np

NDArrays = list[np.ndarray]


def clip_update(delta: NDArrays, clip_norm: float) -> tuple[NDArrays, float]:
    """Scale ``delta`` so its global L2 norm is at most ``clip_norm``.

    Returns the (possibly scaled) update and its original norm.
    """
    if clip_norm <= 0:
        raise ValueError("clip_norm must be positive")
    norm = float(np.sqrt(sum(float(np.sum(a**2)) for a in delta)))
    if norm <= clip_norm or norm == 0.0:
        return [a.copy() for a in delta], norm
    scale = clip_norm / norm
    return [a * scale for a in delta], norm


def gaussian_sigma(epsilon: float, delta: float, sensitivity: float) -> float:
    """Noise scale for the Gaussian mechanism: sigma = sqrt(2 ln(1.25/delta)) * S / eps."""
    if epsilon <= 0 or not 0 < delta < 1 or sensitivity <= 0:
        raise ValueError("require epsilon > 0, 0 < delta < 1, sensitivity > 0")
    return float(np.sqrt(2.0 * np.log(1.25 / delta)) * sensitivity / epsilon)


def apply_dp(
    delta: NDArrays,
    epsilon: float,
    dp_delta: float = 1e-5,
    clip_norm: float = 1.0,
    rng: np.random.Generator | None = None,
) -> tuple[NDArrays, float]:
    """Clip a client delta and add calibrated Gaussian noise.

    Returns the privatised update and the pre-clip norm (logged for
    observability; the norm itself is not released to other clients).
    """
    rng = rng or np.random.default_rng()
    clipped, norm = clip_update(delta, clip_norm)
    sigma = gaussian_sigma(epsilon, dp_delta, clip_norm)
    noised = [a + rng.normal(0.0, sigma, size=a.shape) for a in clipped]
    return noised, norm


class SecureAggregator:
    """Pairwise additive masking over a fixed roster of client ids.

    Each unordered pair ``(i, j)`` deterministically derives a mask seed from
    the round seed; the lower id adds the mask, the higher id subtracts it.
    Summing all masked updates cancels every mask exactly, so the server
    only ever sees the aggregate.
    """

    def __init__(self, client_ids: list[int], round_seed: int):
        if len(set(client_ids)) != len(client_ids):
            raise ValueError("client ids must be unique")
        self.client_ids = sorted(client_ids)
        self.round_seed = round_seed

    def _pair_rng(self, a: int, b: int) -> np.random.Generator:
        lo, hi = min(a, b), max(a, b)
        digest = hashlib.sha256(f"{self.round_seed}:{lo}:{hi}".encode()).digest()
        return np.random.default_rng(int.from_bytes(digest[:8], "big"))

    def mask(self, client_id: int, update: NDArrays) -> NDArrays:
        if client_id not in self.client_ids:
            raise ValueError(f"unknown client id {client_id}")
        masked = [a.astype(np.float64, copy=True) for a in update]
        for other in self.client_ids:
            if other == client_id:
                continue
            rng = self._pair_rng(client_id, other)
            sign = 1.0 if client_id < other else -1.0
            for arr in masked:
                arr += sign * rng.standard_normal(arr.shape)
        return masked

    @staticmethod
    def unmask_sum(masked_updates: list[NDArrays]) -> NDArrays:
        """Sum masked updates; pairwise masks cancel, yielding the true sum."""
        if not masked_updates:
            raise ValueError("no updates")
        total = [np.zeros_like(a) for a in masked_updates[0]]
        for update in masked_updates:
            for i, arr in enumerate(update):
                total[i] += arr
        return total
