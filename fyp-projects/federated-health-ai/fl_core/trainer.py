"""Local training and evaluation for a single federated client."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fl_core.metrics import accuracy, bce_loss, roc_auc
from fl_core.nn import MLP, Adam


@dataclass
class EvalResult:
    loss: float
    accuracy: float
    auc: float


def evaluate(model: MLP, X: np.ndarray, y: np.ndarray) -> EvalResult:
    prob = model.predict_proba(X)
    return EvalResult(loss=bce_loss(y, prob), accuracy=accuracy(y, prob), auc=roc_auc(y, prob))


def train_local(
    model: MLP,
    X: np.ndarray,
    y: np.ndarray,
    epochs: int = 1,
    batch_size: int = 32,
    lr: float = 1e-3,
    prox_mu: float = 0.0,
    seed: int = 0,
) -> float:
    """Train ``model`` in place on a client's local shard; returns final loss.

    ``prox_mu`` > 0 enables the FedProx proximal term, pulling local weights
    towards the global weights the round started from — this stabilises
    training on heterogeneous (non-IID) hospitals.
    """
    if epochs < 1:
        raise ValueError("epochs must be >= 1")
    global_params = model.get_parameters() if prox_mu > 0 else None
    opt = Adam(model, lr=lr)
    rng = np.random.default_rng(seed)
    n = len(X)
    loss = 0.0
    for _epoch in range(epochs):
        order = rng.permutation(n)
        losses: list[float] = []
        for start in range(0, n, batch_size):
            batch = order[start : start + batch_size]
            loss_b = model.loss_and_backward(X[batch], y[batch])
            if global_params is not None and prox_mu > 0:
                _add_prox_grads(model, global_params, prox_mu)
                loss_b += _prox_penalty(model, global_params, prox_mu)
            opt.step()
            losses.append(loss_b)
        loss = float(np.mean(losses))
    return loss


def _add_prox_grads(model: MLP, global_params: list[np.ndarray], mu: float) -> None:
    current = model.get_parameters()
    grads = model.gradients()
    for g, p, gp in zip(grads, current, global_params):
        g += mu * (p - gp)


def _prox_penalty(model: MLP, global_params: list[np.ndarray], mu: float) -> float:
    current = model.get_parameters()
    return float(0.5 * mu * sum(np.sum((p - gp) ** 2) for p, gp in zip(current, global_params)))
