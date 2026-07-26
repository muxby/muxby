"""fl_core — federated learning engine for the federated-health-ai platform.

The numerical core (models, aggregation, privacy) is implemented against
plain ``numpy.ndarray`` parameter lists (Flower's ``NDArrays`` convention),
so the same aggregation/privacy code drives both the in-process simulation
engine used by the API server and the real Flower-based distributed
deployment (``flower_client`` / ``flower_server``).
"""

from fl_core.data import (
    FeatureScaler,
    generate_patients,
    partition_dirichlet,
    train_test_split,
    FEATURE_NAMES,
)
from fl_core.nn import MLP, Adam
from fl_core.aggregation import fedavg, weighted_metric
from fl_core.privacy import clip_update, gaussian_sigma, apply_dp, SecureAggregator
from fl_core.simulation import FederatedSimulation, RoundConfig

__all__ = [
    "FeatureScaler",
    "generate_patients",
    "partition_dirichlet",
    "train_test_split",
    "FEATURE_NAMES",
    "MLP",
    "Adam",
    "fedavg",
    "weighted_metric",
    "clip_update",
    "gaussian_sigma",
    "apply_dp",
    "SecureAggregator",
    "FederatedSimulation",
    "RoundConfig",
]
