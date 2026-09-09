"""Validate attitude representation conversions for mutual consistency."""

from __future__ import annotations

import math

import numpy as np
import pytest
from attitude3d.exceptions import InvalidAttitudeInputError
from attitude3d.rotations import (
    dcm_to_euler,
    dcm_to_quaternion,
    euler_to_dcm,
    euler_to_quaternion,
    quaternion_conjugate,
    quaternion_derivative,
    quaternion_multiply,
    quaternion_normalize,
    quaternion_to_dcm,
    quaternion_to_euler,
)

_TEST_ANGLES_DEG = [(0, 0, 0), (15, -10, 30), (45, 20, -60), (170, 5, -5), (-30, 89, 179)]


@pytest.mark.parametrize("roll,pitch,yaw", _TEST_ANGLES_DEG)
def test_euler_dcm_round_trip(roll: float, pitch: float, yaw: float) -> None:
    r, p, y = math.radians(roll), math.radians(pitch), math.radians(yaw)
    dcm = euler_to_dcm(r, p, y)
    r2, p2, y2 = dcm_to_euler(dcm)
    assert math.isclose(r2, r, abs_tol=1e-9)
    assert math.isclose(p2, p, abs_tol=1e-9)
    assert math.isclose(y2, y, abs_tol=1e-9)


def test_euler_to_dcm_identity_at_zero_angles() -> None:
    assert np.allclose(euler_to_dcm(0.0, 0.0, 0.0), np.eye(3))


def test_dcm_is_orthonormal() -> None:
    """A valid DCM satisfies L @ L.T = I (it's a rotation, preserves lengths)."""
    dcm = euler_to_dcm(math.radians(20), math.radians(-35), math.radians(110))
    assert np.allclose(dcm @ dcm.T, np.eye(3), atol=1e-9)


def test_dcm_to_euler_rejects_bad_shape() -> None:
    with pytest.raises(InvalidAttitudeInputError):
        dcm_to_euler(np.eye(2))


@pytest.mark.parametrize("roll,pitch,yaw", _TEST_ANGLES_DEG)
def test_euler_to_quaternion_is_unit_norm(roll: float, pitch: float, yaw: float) -> None:
    q = euler_to_quaternion(math.radians(roll), math.radians(pitch), math.radians(yaw))
    assert math.isclose(float(np.linalg.norm(q)), 1.0, abs_tol=1e-9)


@pytest.mark.parametrize("roll,pitch,yaw", _TEST_ANGLES_DEG)
def test_euler_quaternion_dcm_are_mutually_consistent(
    roll: float, pitch: float, yaw: float
) -> None:
    """euler->dcm and euler->quaternion->dcm must give the same rotation matrix."""
    r, p, y = math.radians(roll), math.radians(pitch), math.radians(yaw)
    dcm_direct = euler_to_dcm(r, p, y)
    q = euler_to_quaternion(r, p, y)
    dcm_via_quat = quaternion_to_dcm(q)
    assert np.allclose(dcm_direct, dcm_via_quat, atol=1e-9)


@pytest.mark.parametrize("roll,pitch,yaw", _TEST_ANGLES_DEG)
def test_quaternion_euler_round_trip(roll: float, pitch: float, yaw: float) -> None:
    r, p, y = math.radians(roll), math.radians(pitch), math.radians(yaw)
    q = euler_to_quaternion(r, p, y)
    r2, p2, y2 = quaternion_to_euler(q)
    assert math.isclose(r2, r, abs_tol=1e-9)
    assert math.isclose(p2, p, abs_tol=1e-9)
    assert math.isclose(y2, y, abs_tol=1e-9)


@pytest.mark.parametrize("roll,pitch,yaw", _TEST_ANGLES_DEG)
def test_dcm_quaternion_round_trip(roll: float, pitch: float, yaw: float) -> None:
    """Includes a near-180-degree case that a naive trace-only method would fail on."""
    r, p, y = math.radians(roll), math.radians(pitch), math.radians(yaw)
    dcm = euler_to_dcm(r, p, y)
    q = dcm_to_quaternion(dcm)
    dcm2 = quaternion_to_dcm(q)
    assert np.allclose(dcm, dcm2, atol=1e-9)
    assert math.isclose(float(np.linalg.norm(q)), 1.0, abs_tol=1e-9)


def test_dcm_to_quaternion_rejects_bad_shape() -> None:
    with pytest.raises(InvalidAttitudeInputError):
        dcm_to_quaternion(np.eye(4))


def test_quaternion_multiply_identity() -> None:
    identity = np.array([1.0, 0.0, 0.0, 0.0])
    q = euler_to_quaternion(0.3, -0.2, 0.5)
    assert np.allclose(quaternion_multiply(identity, q), q)
    assert np.allclose(quaternion_multiply(q, identity), q)


def test_quaternion_multiply_with_conjugate_gives_identity() -> None:
    q = euler_to_quaternion(0.3, -0.2, 0.5)
    q_conj = quaternion_conjugate(q)
    product = quaternion_multiply(q, q_conj)
    assert np.allclose(product, [1.0, 0.0, 0.0, 0.0], atol=1e-9)


def test_quaternion_conjugate_negates_vector_part() -> None:
    q = np.array([0.5, 0.5, 0.5, 0.5])
    assert np.allclose(quaternion_conjugate(q), [0.5, -0.5, -0.5, -0.5])


def test_quaternion_normalize_produces_unit_norm() -> None:
    q = np.array([2.0, 1.0, 1.0, 1.0])
    normalized = quaternion_normalize(q)
    assert math.isclose(float(np.linalg.norm(normalized)), 1.0, abs_tol=1e-9)


def test_quaternion_normalize_rejects_zero_quaternion() -> None:
    with pytest.raises(InvalidAttitudeInputError):
        quaternion_normalize(np.array([0.0, 0.0, 0.0, 0.0]))


def test_quaternion_derivative_matches_hamilton_product_formula() -> None:
    q = euler_to_quaternion(0.3, -0.2, 0.5)
    omega = np.array([0.1, -0.05, 0.2])
    expected = 0.5 * quaternion_multiply(q, np.array([0.0, *omega]))
    assert np.allclose(quaternion_derivative(q, omega), expected, atol=1e-12)


def test_quaternion_derivative_integration_matches_known_rotation() -> None:
    """Integrating a constant roll rate of 1 rad/s for 1s should match a 1 rad roll quaternion."""
    q = np.array([1.0, 0.0, 0.0, 0.0])
    dt = 1e-4
    omega = np.array([1.0, 0.0, 0.0])
    for _ in range(10_000):
        q = q + quaternion_derivative(q, omega) * dt
        q = quaternion_normalize(q)
    expected = euler_to_quaternion(1.0, 0.0, 0.0)
    assert np.allclose(q, expected, atol=1e-3)


def test_quaternion_derivative_rejects_bad_shapes() -> None:
    q = np.array([1.0, 0.0, 0.0, 0.0])
    with pytest.raises(InvalidAttitudeInputError):
        quaternion_derivative(q, np.array([1.0, 0.0]))
