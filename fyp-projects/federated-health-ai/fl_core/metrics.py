"""Evaluation metrics implemented without external dependencies."""

from __future__ import annotations

import numpy as np


def accuracy(y_true: np.ndarray, y_prob: np.ndarray, threshold: float = 0.5) -> float:
    return float(np.mean((y_prob >= threshold) == (y_true >= 0.5)))


def roc_auc(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    """Rank-based AUC (equivalent to the Mann-Whitney U statistic).

    Returns 0.5 when only one class is present, matching the convention of
    an uninformative classifier rather than raising.
    """
    y_true = np.asarray(y_true, dtype=np.float64)
    pos = y_true >= 0.5
    n_pos = int(pos.sum())
    n_neg = len(y_true) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5
    order = np.argsort(y_prob, kind="mergesort")
    ranks = np.empty(len(y_prob), dtype=np.float64)
    sorted_probs = y_prob[order]
    # Average ranks over ties.
    i = 0
    while i < len(sorted_probs):
        j = i
        while j + 1 < len(sorted_probs) and sorted_probs[j + 1] == sorted_probs[i]:
            j += 1
        ranks[order[i : j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return float((ranks[pos].sum() - n_pos * (n_pos + 1) / 2.0) / (n_pos * n_neg))


def bce_loss(y_true: np.ndarray, y_prob: np.ndarray, eps: float = 1e-7) -> float:
    p = np.clip(y_prob, eps, 1 - eps)
    return float(-np.mean(y_true * np.log(p) + (1 - y_true) * np.log(1 - p)))
