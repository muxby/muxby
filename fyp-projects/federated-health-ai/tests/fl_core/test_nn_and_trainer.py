import numpy as np
import pytest

from fl_core.data import NUM_FEATURES, FeatureScaler, generate_patients, train_test_split
from fl_core.metrics import accuracy, bce_loss, roc_auc
from fl_core.nn import MLP, Adam
from fl_core.trainer import evaluate, train_local


@pytest.fixture(scope="module")
def cohort():
    X, y = generate_patients(1500, seed=42)
    scaler = FeatureScaler.fit(X)
    return train_test_split(scaler.transform(X), y, test_fraction=0.2, seed=42)


def test_mlp_forward_shape_and_probability_range():
    model = MLP(NUM_FEATURES, seed=0)
    X = np.random.default_rng(0).normal(size=(17, NUM_FEATURES))
    prob = model.predict_proba(X)
    assert prob.shape == (17,)
    assert np.all((prob > 0) & (prob < 1))


def test_parameter_roundtrip_preserves_outputs():
    m1 = MLP(NUM_FEATURES, seed=1)
    m2 = MLP(NUM_FEATURES, seed=2)
    X = np.random.default_rng(3).normal(size=(8, NUM_FEATURES))
    assert not np.allclose(m1.predict_proba(X), m2.predict_proba(X))
    m2.set_parameters(m1.get_parameters())
    np.testing.assert_allclose(m1.predict_proba(X), m2.predict_proba(X))


def test_set_parameters_validates_shapes():
    model = MLP(NUM_FEATURES, seed=0)
    params = model.get_parameters()
    with pytest.raises(ValueError):
        model.set_parameters(params[:-1])
    bad = [p.copy() for p in params]
    bad[0] = np.zeros((3, 3))
    with pytest.raises(ValueError):
        model.set_parameters(bad)


def test_backprop_gradients_match_numerical_gradients():
    """Finite-difference check of the analytic gradients on a tiny model."""
    model = MLP(4, hidden=(5,), seed=0)
    rng = np.random.default_rng(0)
    X = rng.normal(size=(12, 4))
    y = (rng.random(12) < 0.5).astype(float)

    model.loss_and_backward(X, y)
    analytic = [g.copy() for g in model.gradients()]

    eps = 1e-6
    params = model.get_parameters()
    for pi, p in enumerate(params):
        flat = p.ravel()
        for k in range(0, flat.size, max(1, flat.size // 5)):  # sample entries
            orig = flat[k]
            flat[k] = orig + eps
            model.set_parameters(params)
            lp = _loss_only(model, X, y)
            flat[k] = orig - eps
            model.set_parameters(params)
            lm = _loss_only(model, X, y)
            flat[k] = orig
            model.set_parameters(params)
            numeric = (lp - lm) / (2 * eps)
            assert abs(numeric - analytic[pi].ravel()[k]) < 1e-4


def _loss_only(model: MLP, X, y) -> float:
    logits = model.forward(X)
    return float(
        np.mean(np.maximum(logits, 0) - logits * y + np.log1p(np.exp(-np.abs(logits))))
    )


def test_adam_reduces_loss(cohort):
    X_tr, y_tr, _, _ = cohort
    model = MLP(NUM_FEATURES, seed=0)
    before = evaluate(model, X_tr, y_tr).loss
    train_local(model, X_tr, y_tr, epochs=3, lr=1e-3, seed=0)
    after = evaluate(model, X_tr, y_tr).loss
    assert after < before


def test_training_beats_chance_on_held_out_data(cohort):
    X_tr, y_tr, X_te, y_te = cohort
    model = MLP(NUM_FEATURES, seed=0)
    train_local(model, X_tr, y_tr, epochs=8, lr=2e-3, seed=0)
    ev = evaluate(model, X_te, y_te)
    assert ev.auc > 0.75
    assert ev.accuracy > 0.65


def test_fedprox_term_keeps_weights_closer_to_global(cohort):
    X_tr, y_tr, _, _ = cohort
    plain = MLP(NUM_FEATURES, seed=0)
    prox = MLP(NUM_FEATURES, seed=0)
    start = plain.get_parameters()
    train_local(plain, X_tr, y_tr, epochs=3, lr=5e-3, prox_mu=0.0, seed=1)
    train_local(prox, X_tr, y_tr, epochs=3, lr=5e-3, prox_mu=1.0, seed=1)
    drift_plain = sum(np.linalg.norm(a - b) for a, b in zip(plain.get_parameters(), start))
    drift_prox = sum(np.linalg.norm(a - b) for a, b in zip(prox.get_parameters(), start))
    assert drift_prox < drift_plain


def test_train_local_rejects_zero_epochs(cohort):
    X_tr, y_tr, _, _ = cohort
    with pytest.raises(ValueError):
        train_local(MLP(NUM_FEATURES), X_tr, y_tr, epochs=0)


# ---- metrics ------------------------------------------------------------
def test_accuracy_metric():
    y = np.array([1, 0, 1, 0])
    p = np.array([0.9, 0.2, 0.4, 0.6])
    assert accuracy(y, p) == 0.5


def test_roc_auc_perfect_and_inverted():
    y = np.array([0, 0, 1, 1])
    assert roc_auc(y, np.array([0.1, 0.2, 0.8, 0.9])) == 1.0
    assert roc_auc(y, np.array([0.9, 0.8, 0.2, 0.1])) == 0.0


def test_roc_auc_handles_ties_and_single_class():
    y = np.array([0, 1, 0, 1])
    assert roc_auc(y, np.array([0.5, 0.5, 0.5, 0.5])) == 0.5
    assert roc_auc(np.ones(4), np.random.default_rng(0).random(4)) == 0.5


def test_bce_loss_is_low_for_confident_correct_predictions():
    y = np.array([1.0, 0.0])
    assert bce_loss(y, np.array([0.99, 0.01])) < 0.05
    assert bce_loss(y, np.array([0.01, 0.99])) > 2.0
