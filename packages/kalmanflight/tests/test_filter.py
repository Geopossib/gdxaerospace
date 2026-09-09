"""Validate the discrete linear Kalman filter against hand-computed and known scenarios."""

from __future__ import annotations

import math

import numpy as np
import pytest
from kalmanflight.exceptions import InvalidKalmanFilterInputError
from kalmanflight.filter import KalmanFilter


def _scalar_filter(
    x0: float = 0.0, p0: float = 1.0, q: float = 0.0, r: float = 1.0
) -> KalmanFilter:
    return KalmanFilter(
        x0=np.array([x0]),
        p0=np.array([[p0]]),
        f=np.array([[1.0]]),
        h=np.array([[1.0]]),
        q=np.array([[q]]),
        r=np.array([[r]]),
    )


def test_scalar_predict_with_zero_process_noise_leaves_state_and_covariance_unchanged() -> None:
    kf = _scalar_filter(x0=3.0, p0=2.0, q=0.0)
    kf.predict()
    assert math.isclose(kf.x[0], 3.0)
    assert math.isclose(kf.p[0, 0], 2.0)


def test_scalar_predict_adds_process_noise_to_covariance() -> None:
    kf = _scalar_filter(x0=0.0, p0=1.0, q=0.5)
    kf.predict()
    assert math.isclose(kf.p[0, 0], 1.5)


def test_scalar_update_matches_hand_calculation() -> None:
    """K = P/(P+R) = 0.5; x = 0 + 0.5*(1-0) = 0.5; P = (1-0.5)*1 = 0.5."""
    kf = _scalar_filter(x0=0.0, p0=1.0, q=0.0, r=1.0)
    kf.predict()
    kf.update(np.array([1.0]))
    assert math.isclose(kf.x[0], 0.5, rel_tol=1e-9)
    assert math.isclose(kf.p[0, 0], 0.5, rel_tol=1e-9)


def test_update_estimate_moves_toward_measurement() -> None:
    kf = _scalar_filter(x0=0.0, p0=1.0, q=0.0, r=1.0)
    kf.predict()
    kf.update(np.array([10.0]))
    assert 0.0 < kf.x[0] < 10.0


def test_repeated_updates_converge_toward_true_constant_value() -> None:
    """Error to the true (static) value should shrink monotonically as measurements accumulate."""
    kf = _scalar_filter(x0=0.0, p0=10.0, q=0.0, r=1.0)
    true_value = 5.0
    errors = []
    for _ in range(20):
        kf.predict()
        kf.update(np.array([true_value]))
        errors.append(abs(kf.x[0] - true_value))
    assert errors == sorted(errors, reverse=True)
    assert errors[-1] < 0.05


def test_covariance_shrinks_monotonically_with_repeated_updates() -> None:
    """Uncertainty should never increase from taking more (informative) measurements."""
    kf = _scalar_filter(x0=0.0, p0=10.0, q=0.0, r=1.0)
    covariances = []
    for _ in range(10):
        kf.predict()
        kf.update(np.array([5.0]))
        covariances.append(kf.p[0, 0])
    assert covariances == sorted(covariances, reverse=True)


def test_covariance_stays_symmetric_and_positive() -> None:
    """The Joseph-form update should keep P symmetric and positive semi-definite."""
    kf = _scalar_filter(x0=0.0, p0=10.0, q=0.1, r=1.0)
    for _ in range(20):
        kf.predict()
        kf.update(np.array([3.0]))
    assert np.allclose(kf.p, kf.p.T)
    assert kf.p[0, 0] >= 0


def test_constant_velocity_tracking_matches_zarchan_style_scenario() -> None:
    """Classic 2-state constant-velocity tracker: position+velocity from noisy
    position-only measurements should converge close to the true trajectory."""
    dt = 1.0
    f = np.array([[1.0, dt], [0.0, 1.0]])
    h = np.array([[1.0, 0.0]])
    q = np.array([[0.01, 0.0], [0.0, 0.01]])
    r = np.array([[4.0]])
    kf = KalmanFilter(x0=np.array([0.0, 0.0]), p0=np.eye(2) * 100.0, f=f, h=h, q=q, r=r)

    true_position, true_velocity = 0.0, 2.0
    rng = np.random.default_rng(42)
    for _ in range(50):
        true_position += true_velocity * dt
        measurement = true_position + rng.normal(0, 2.0)
        kf.predict()
        kf.update(np.array([measurement]))

    assert math.isclose(kf.x[0], true_position, abs_tol=15.0)
    assert math.isclose(kf.x[1], true_velocity, abs_tol=1.0)


def test_predict_with_control_input_matches_formula() -> None:
    f = np.array([[1.0]])
    b = np.array([[2.0]])
    kf = KalmanFilter(
        x0=np.array([0.0]),
        p0=np.array([[1.0]]),
        f=f,
        h=np.array([[1.0]]),
        q=np.array([[0.0]]),
        r=np.array([[1.0]]),
    )
    kf.predict(u=np.array([3.0]), b=b)
    assert math.isclose(kf.x[0], 6.0, rel_tol=1e-9)  # F*x + B*u = 1*0 + 2*3 = 6


def test_predict_requires_b_when_u_given() -> None:
    kf = _scalar_filter()
    with pytest.raises(InvalidKalmanFilterInputError):
        kf.predict(u=np.array([1.0]))


def test_constructor_rejects_mismatched_shapes() -> None:
    with pytest.raises(InvalidKalmanFilterInputError):
        KalmanFilter(
            x0=np.array([0.0, 0.0]),
            p0=np.eye(3),  # wrong shape: should be (2,2)
            f=np.eye(2),
            h=np.array([[1.0, 0.0]]),
            q=np.eye(2),
            r=np.array([[1.0]]),
        )
    with pytest.raises(InvalidKalmanFilterInputError):
        KalmanFilter(
            x0=np.array([0.0]),
            p0=np.array([[1.0]]),
            f=np.array([[1.0]]),
            h=np.array([[1.0, 0.0]]),  # wrong number of columns
            q=np.array([[1.0]]),
            r=np.array([[1.0]]),
        )
