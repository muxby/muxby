import numpy as np
import pytest

from fl_core.aggregation import apply_delta, fedavg, update_norm, weighted_metric
from fl_core.privacy import SecureAggregator, apply_dp, clip_update, gaussian_sigma
from fl_core.serialization import params_from_bytes, params_to_bytes


def _params(scale: float) -> list[np.ndarray]:
    return [np.full((2, 3), scale), np.full(3, scale * 2)]


# ---- aggregation --------------------------------------------------------
def test_fedavg_weighted_average():
    agg = fedavg([(_params(1.0), 100), (_params(3.0), 300)])
    np.testing.assert_allclose(agg[0], np.full((2, 3), 2.5))
    np.testing.assert_allclose(agg[1], np.full(3, 5.0))


def test_fedavg_rejects_empty_and_inconsistent():
    with pytest.raises(ValueError):
        fedavg([])
    with pytest.raises(ValueError):
        fedavg([(_params(1.0), 10), ([_params(1.0)[0]], 10)])
    with pytest.raises(ValueError):
        fedavg([(_params(1.0), 0)])


def test_apply_delta_with_server_lr():
    out = apply_delta(_params(1.0), _params(2.0), server_lr=0.5)
    np.testing.assert_allclose(out[0], np.full((2, 3), 2.0))


def test_weighted_metric():
    assert weighted_metric([(0.8, 100), (0.6, 300)]) == pytest.approx(0.65)


def test_update_norm():
    delta = [np.array([3.0]), np.array([4.0])]
    assert update_norm(delta) == pytest.approx(5.0)


# ---- clipping / DP ------------------------------------------------------
def test_clip_update_scales_only_when_needed():
    delta = [np.array([3.0]), np.array([4.0])]  # norm 5
    clipped, norm = clip_update(delta, clip_norm=2.5)
    assert norm == pytest.approx(5.0)
    assert update_norm(clipped) == pytest.approx(2.5)
    same, _ = clip_update(delta, clip_norm=10.0)
    np.testing.assert_allclose(same[0], delta[0])


def test_gaussian_sigma_matches_analytic_formula():
    sigma = gaussian_sigma(epsilon=1.0, delta=1e-5, sensitivity=1.0)
    assert sigma == pytest.approx(np.sqrt(2 * np.log(1.25e5)), rel=1e-9)
    with pytest.raises(ValueError):
        gaussian_sigma(0, 1e-5, 1.0)
    with pytest.raises(ValueError):
        gaussian_sigma(1.0, 2.0, 1.0)


def test_apply_dp_bounds_norm_and_adds_noise():
    rng = np.random.default_rng(0)
    delta = [np.ones((50, 50)) * 0.5]
    noised, pre_norm = apply_dp(delta, epsilon=8.0, clip_norm=1.0, rng=rng)
    assert pre_norm == pytest.approx(update_norm(delta))
    assert not np.allclose(noised[0], delta[0])


def test_dp_noise_scale_grows_as_epsilon_shrinks():
    delta = [np.zeros(10_000)]
    strong = apply_dp(delta, epsilon=0.5, clip_norm=1.0, rng=np.random.default_rng(1))[0][0]
    weak = apply_dp(delta, epsilon=10.0, clip_norm=1.0, rng=np.random.default_rng(1))[0][0]
    assert strong.std() > weak.std() * 5


# ---- secure aggregation -------------------------------------------------
def test_secure_aggregation_masks_cancel_exactly():
    rng = np.random.default_rng(0)
    updates = {cid: [rng.normal(size=(4, 4)), rng.normal(size=4)] for cid in [1, 2, 3]}
    agg = SecureAggregator([1, 2, 3], round_seed=99)
    masked = [agg.mask(cid, upd) for cid, upd in updates.items()]
    summed = SecureAggregator.unmask_sum(masked)
    expected = [sum(updates[c][i] for c in updates) for i in range(2)]
    for got, exp in zip(summed, expected):
        np.testing.assert_allclose(got, exp, atol=1e-9)


def test_secure_aggregation_hides_individual_updates():
    update = [np.zeros((8, 8))]
    agg = SecureAggregator([1, 2, 3], round_seed=5)
    masked = agg.mask(1, update)
    assert np.abs(masked[0]).max() > 0.1  # zero update is unrecognisable


def test_secure_aggregator_validates_ids():
    with pytest.raises(ValueError):
        SecureAggregator([1, 1, 2], round_seed=0)
    agg = SecureAggregator([1, 2], round_seed=0)
    with pytest.raises(ValueError):
        agg.mask(3, [np.zeros(2)])
    with pytest.raises(ValueError):
        SecureAggregator.unmask_sum([])


# ---- serialization ------------------------------------------------------
def test_params_bytes_roundtrip():
    params = [np.random.default_rng(0).normal(size=(10, 5)), np.arange(5, dtype=np.float64)]
    blob = params_to_bytes(params)
    restored = params_from_bytes(blob)
    assert len(restored) == 2
    for a, b in zip(params, restored):
        np.testing.assert_array_equal(a, b)
