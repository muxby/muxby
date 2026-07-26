import numpy as np
import pytest

from fl_core.data import (
    FEATURE_NAMES,
    FeatureScaler,
    generate_patients,
    partition_dirichlet,
    train_test_split,
)


def test_generate_patients_shapes_and_determinism():
    X1, y1 = generate_patients(500, seed=7)
    X2, y2 = generate_patients(500, seed=7)
    assert X1.shape == (500, len(FEATURE_NAMES))
    assert y1.shape == (500,)
    np.testing.assert_array_equal(X1, X2)
    np.testing.assert_array_equal(y1, y2)


def test_generate_patients_clinically_plausible_ranges():
    X, y = generate_patients(2000, seed=1)
    age, systolic, bmi = X[:, 0], X[:, 2], X[:, 6]
    assert age.min() >= 30 and age.max() <= 90
    assert systolic.min() >= 90 and systolic.max() <= 210
    assert bmi.min() >= 16 and bmi.max() <= 55
    assert set(np.unique(X[:, 1])) <= {0.0, 1.0}  # sex is binary
    assert 0.05 < y.mean() < 0.95  # both classes present in bulk


def test_risk_shift_changes_prevalence():
    _, y_low = generate_patients(3000, seed=3, risk_shift=-1.0)
    _, y_high = generate_patients(3000, seed=3, risk_shift=1.0)
    assert y_high.mean() > y_low.mean() + 0.1


def test_scaler_standardizes_continuous_and_skips_binary():
    X, _ = generate_patients(1000, seed=5)
    scaler = FeatureScaler.fit(X)
    Xs = scaler.transform(X)
    assert abs(Xs[:, 0].mean()) < 1e-8  # age centred
    assert abs(Xs[:, 0].std() - 1.0) < 1e-6
    np.testing.assert_array_equal(Xs[:, 1], X[:, 1])  # sex untouched
    np.testing.assert_array_equal(Xs[:, 8], X[:, 8])  # smoker untouched


def test_scaler_roundtrip_serialization():
    X, _ = generate_patients(200, seed=5)
    scaler = FeatureScaler.fit(X)
    restored = FeatureScaler.from_arrays(scaler.to_arrays())
    np.testing.assert_array_equal(scaler.transform(X), restored.transform(X))


def test_train_test_split_disjoint_and_sized():
    X, y = generate_patients(1000, seed=2)
    X_tr, y_tr, X_te, y_te = train_test_split(X, y, test_fraction=0.25, seed=0)
    assert len(X_te) == 250 and len(X_tr) == 750
    assert len(y_tr) == 750 and len(y_te) == 250


def test_train_test_split_rejects_bad_fraction():
    X, y = generate_patients(50, seed=2)
    with pytest.raises(ValueError):
        train_test_split(X, y, test_fraction=1.5)


def test_dirichlet_partition_covers_all_indices_disjointly():
    _, y = generate_patients(2000, seed=9)
    parts = partition_dirichlet(y, n_clients=4, alpha=0.5, seed=9)
    all_idx = np.concatenate(parts)
    assert len(all_idx) == len(y)
    assert len(np.unique(all_idx)) == len(y)
    assert all(len(p) >= 10 for p in parts)


def test_dirichlet_partition_is_label_skewed():
    _, y = generate_patients(4000, seed=11)
    parts = partition_dirichlet(y, n_clients=4, alpha=0.1, seed=11)
    prevalences = [y[p].mean() for p in parts]
    assert max(prevalences) - min(prevalences) > 0.05  # heterogeneous hospitals


def test_single_client_partition_is_identity():
    _, y = generate_patients(100, seed=1)
    (part,) = partition_dirichlet(y, n_clients=1)
    np.testing.assert_array_equal(part, np.arange(100))
