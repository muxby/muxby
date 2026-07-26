"""Synthetic-but-realistic cardiovascular risk dataset and non-IID partitioning.

Real patient data cannot ship with the repository, so the platform generates a
clinically plausible cohort: feature distributions and the latent risk model
are loosely based on Framingham-style risk factors. The generator is fully
deterministic given a seed, which keeps every test and every federated round
reproducible.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

FEATURE_NAMES = [
    "age",
    "sex",
    "systolic_bp",
    "diastolic_bp",
    "cholesterol",
    "hdl",
    "bmi",
    "glucose",
    "smoker",
    "family_history",
]

NUM_FEATURES = len(FEATURE_NAMES)


def generate_patients(
    n: int,
    seed: int = 0,
    risk_shift: float = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate ``n`` synthetic patients.

    Returns ``(X, y)`` where ``X`` has shape ``(n, NUM_FEATURES)`` in raw
    clinical units and ``y`` is a 0/1 cardiovascular-event label.

    ``risk_shift`` biases the latent risk score, letting callers create
    hospitals with sicker or healthier populations (covariate shift between
    federated clients).
    """
    rng = np.random.default_rng(seed)

    age = rng.normal(58, 12, n).clip(30, 90)
    sex = rng.integers(0, 2, n).astype(float)  # 1 = male
    systolic = rng.normal(128, 18, n).clip(90, 210)
    diastolic = (systolic * 0.62 + rng.normal(2, 7, n)).clip(50, 130)
    cholesterol = rng.normal(205, 38, n).clip(110, 360)
    hdl = rng.normal(52, 14, n).clip(20, 110)
    bmi = rng.normal(27.5, 4.8, n).clip(16, 55)
    glucose = rng.normal(102, 24, n).clip(60, 300)
    smoker = (rng.random(n) < 0.22).astype(float)
    family_history = (rng.random(n) < 0.30).astype(float)

    X = np.stack(
        [age, sex, systolic, diastolic, cholesterol, hdl, bmi, glucose, smoker, family_history],
        axis=1,
    )

    # Latent Framingham-style log-odds: standardized risk factors with
    # a smoking x age interaction and protective HDL term.
    z = (
        0.055 * (age - 58)
        + 0.35 * sex
        + 0.030 * (systolic - 128)
        + 0.012 * (cholesterol - 205)
        - 0.028 * (hdl - 52)
        + 0.055 * (bmi - 27.5)
        + 0.011 * (glucose - 102)
        + 0.85 * smoker
        + 0.55 * family_history
        + 0.010 * smoker * (age - 58)
        + risk_shift
        - 1.1
    )
    prob = 1.0 / (1.0 + np.exp(-z))
    y = (rng.random(n) < prob).astype(np.float64)
    return X, y


@dataclass
class FeatureScaler:
    """Per-feature standardization fitted on training data.

    Binary features (sex, smoker, family_history) are left unscaled so the
    prediction API can accept raw clinical values.
    """

    mean: np.ndarray
    std: np.ndarray

    _BINARY_IDX = (1, 8, 9)

    @classmethod
    def fit(cls, X: np.ndarray) -> "FeatureScaler":
        mean = X.mean(axis=0)
        std = X.std(axis=0)
        for i in cls._BINARY_IDX:
            mean[i] = 0.0
            std[i] = 1.0
        std = np.where(std < 1e-8, 1.0, std)
        return cls(mean=mean, std=std)

    def transform(self, X: np.ndarray) -> np.ndarray:
        return (X - self.mean) / self.std

    def to_arrays(self) -> list[np.ndarray]:
        return [self.mean.copy(), self.std.copy()]

    @classmethod
    def from_arrays(cls, arrays: list[np.ndarray]) -> "FeatureScaler":
        return cls(mean=arrays[0].copy(), std=arrays[1].copy())


def train_test_split(
    X: np.ndarray,
    y: np.ndarray,
    test_fraction: float = 0.2,
    seed: int = 0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if not 0.0 < test_fraction < 1.0:
        raise ValueError("test_fraction must be in (0, 1)")
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(X))
    n_test = max(1, int(len(X) * test_fraction))
    test_idx, train_idx = idx[:n_test], idx[n_test:]
    return X[train_idx], y[train_idx], X[test_idx], y[test_idx]


def partition_dirichlet(
    y: np.ndarray,
    n_clients: int,
    alpha: float = 0.5,
    seed: int = 0,
    min_samples: int = 10,
) -> list[np.ndarray]:
    """Label-skewed non-IID partition of sample indices across clients.

    Uses the standard Dirichlet allocation: for every class, a Dirichlet
    draw decides what share of that class each client receives. Lower
    ``alpha`` means more heterogeneous hospitals. Re-draws until every
    client has at least ``min_samples`` samples.
    """
    if n_clients < 1:
        raise ValueError("n_clients must be >= 1")
    if n_clients == 1:
        return [np.arange(len(y))]

    rng = np.random.default_rng(seed)
    classes = np.unique(y)
    for _attempt in range(100):
        client_idx: list[list[int]] = [[] for _ in range(n_clients)]
        for c in classes:
            c_idx = np.where(y == c)[0]
            rng.shuffle(c_idx)
            shares = rng.dirichlet([alpha] * n_clients)
            cuts = (np.cumsum(shares)[:-1] * len(c_idx)).astype(int)
            for client, chunk in enumerate(np.split(c_idx, cuts)):
                client_idx[client].extend(chunk.tolist())
        sizes = [len(ci) for ci in client_idx]
        if min(sizes) >= min_samples:
            return [np.array(sorted(ci), dtype=np.int64) for ci in client_idx]
    raise RuntimeError(
        f"could not build a partition giving every one of {n_clients} clients "
        f">= {min_samples} samples; lower min_samples or raise alpha"
    )
