import numpy as np
import pytest

from fl_core.data import FeatureScaler, generate_patients, partition_dirichlet, train_test_split
from fl_core.simulation import FederatedSimulation, RoundConfig


@pytest.fixture(scope="module")
def federation():
    X, y = generate_patients(3000, seed=42)
    scaler = FeatureScaler.fit(X)
    X_tr, y_tr, X_te, y_te = train_test_split(scaler.transform(X), y, test_fraction=0.25, seed=42)
    parts = partition_dirichlet(y_tr, n_clients=3, alpha=0.8, seed=42)
    clients = {i + 1: (X_tr[p], y_tr[p]) for i, p in enumerate(parts)}
    return clients, (X_te, y_te)


def _run(federation, **overrides):
    clients, test_set = federation
    cfg = RoundConfig(num_rounds=3, local_epochs=2, lr=1e-3, seed=7)
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return FederatedSimulation(clients, test_set, cfg).run()


def test_simulation_produces_history_and_learns(federation):
    result = _run(federation, num_rounds=8)
    assert len(result.history) == 8
    assert result.history[-1].auc > 0.72
    assert result.final_eval is not None
    assert not result.cancelled
    # one update per client per round
    assert len(result.client_updates) == 8 * 3


def test_simulation_is_deterministic(federation):
    r1 = _run(federation)
    r2 = _run(federation)
    for a, b in zip(r1.final_params, r2.final_params):
        np.testing.assert_array_equal(a, b)
    assert [h.accuracy for h in r1.history] == [h.accuracy for h in r2.history]


def test_secure_aggregation_matches_plain_fedavg(federation):
    """Masking must not change the aggregate (up to float error)."""
    plain = _run(federation, secure_aggregation=False)
    masked = _run(federation, secure_aggregation=True)
    for a, b in zip(plain.final_params, masked.final_params):
        np.testing.assert_allclose(a, b, atol=1e-8)


def test_dp_noise_perturbs_but_model_still_learns(federation):
    dp = _run(federation, num_rounds=5, dp_enabled=True, dp_epsilon=50.0, dp_clip_norm=10.0)
    plain = _run(federation, num_rounds=5)
    assert any(
        not np.allclose(a, b) for a, b in zip(dp.final_params, plain.final_params)
    )
    assert dp.history[-1].auc > 0.6  # gentle DP budget still learns


def test_progress_events_are_emitted(federation):
    clients, test_set = federation
    events: list[dict] = []
    cfg = RoundConfig(num_rounds=2, local_epochs=1, seed=1)
    FederatedSimulation(clients, test_set, cfg, progress_cb=events.append).run()
    kinds = {e["type"] for e in events}
    assert kinds == {"round_progress", "client_update"}
    assert sum(e["type"] == "round_progress" for e in events) == 2
    assert sum(e["type"] == "client_update" for e in events) == 2 * len(clients)


def test_cancellation_stops_between_rounds(federation):
    clients, test_set = federation
    calls = {"n": 0}

    def cancel() -> bool:
        calls["n"] += 1
        return calls["n"] > 2  # allow ~2 rounds then cancel

    cfg = RoundConfig(num_rounds=50, local_epochs=1, seed=1)
    result = FederatedSimulation(clients, test_set, cfg, cancel_cb=cancel).run()
    assert result.cancelled
    assert len(result.history) < 50


def test_config_validation():
    with pytest.raises(ValueError):
        RoundConfig(num_rounds=0).validate()
    with pytest.raises(ValueError):
        RoundConfig(local_epochs=0).validate()
    with pytest.raises(ValueError):
        RoundConfig(dp_enabled=True, dp_epsilon=-1).validate()


def test_simulation_requires_clients():
    with pytest.raises(ValueError):
        FederatedSimulation({}, (np.zeros((1, 10)), np.zeros(1)), RoundConfig())


def test_warm_start_from_initial_params(federation):
    clients, test_set = federation
    first = _run(federation, num_rounds=2)
    cfg = RoundConfig(num_rounds=1, local_epochs=1, seed=7)
    warm = FederatedSimulation(clients, test_set, cfg, initial_params=first.final_params).run()
    # warm start should not regress far below the checkpoint it started from
    assert warm.history[-1].auc > first.history[-1].auc - 0.1
