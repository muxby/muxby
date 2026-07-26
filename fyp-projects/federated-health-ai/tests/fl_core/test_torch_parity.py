"""Parity between the NumPy reference model and the PyTorch mirror.

Skipped automatically when torch is not installed (e.g. slim CI images);
the docker-based CI job runs them.
"""

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from fl_core.data import NUM_FEATURES, FeatureScaler, generate_patients, train_test_split
from fl_core.nn import MLP
from fl_core.torch_model import TorchMLP, evaluate_torch, train_torch


def test_torch_model_matches_numpy_model_given_same_parameters():
    ref = MLP(NUM_FEATURES, seed=3)
    mirror = TorchMLP()
    mirror.set_ndarrays(ref.get_parameters())

    X = np.random.default_rng(0).normal(size=(64, NUM_FEATURES))
    ref_logits = ref.forward(X)
    with torch.no_grad():
        torch_logits = mirror(torch.from_numpy(X).float()).numpy()
    np.testing.assert_allclose(ref_logits, torch_logits, atol=1e-4)


def test_ndarray_roundtrip_through_torch():
    ref = MLP(NUM_FEATURES, seed=5)
    mirror = TorchMLP()
    mirror.set_ndarrays(ref.get_parameters())
    back = mirror.get_ndarrays()
    for a, b in zip(ref.get_parameters(), back):
        np.testing.assert_allclose(a, b, atol=1e-6)


def test_torch_training_learns_the_cohort():
    X, y = generate_patients(1200, seed=8)
    scaler = FeatureScaler.fit(X)
    X_tr, y_tr, X_te, y_te = train_test_split(scaler.transform(X), y, test_fraction=0.2, seed=8)
    torch.manual_seed(0)
    model = TorchMLP()
    before_loss, _ = evaluate_torch(model, X_te, y_te)
    train_torch(model, X_tr, y_tr, epochs=6, lr=2e-3)
    after_loss, acc = evaluate_torch(model, X_te, y_te)
    assert after_loss < before_loss
    assert acc > 0.65


def test_set_ndarrays_validates_length():
    mirror = TorchMLP()
    with pytest.raises(ValueError):
        mirror.set_ndarrays(mirror.get_ndarrays()[:-1])
