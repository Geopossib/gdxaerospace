"""Validate rigid-body 6-DOF equations of motion."""

from __future__ import annotations

import math

import numpy as np
import pytest
from attitude3d.rotations import euler_to_dcm
from flightdyn.exceptions import InvalidFlightDynamicsInputError
from flightdyn.rigid_body import (
    G0,
    gravity_body_frame,
    position_derivative,
    rotational_acceleration,
    translational_acceleration,
)


def test_translational_acceleration_reduces_to_newtons_second_law_when_not_rotating() -> None:
    dv = translational_acceleration(
        velocity_body=np.zeros(3),
        angular_velocity_body=np.zeros(3),
        force_body=np.array([2000.0, 0.0, -500.0]),
        mass=1000.0,
    )
    assert np.allclose(dv, np.array([2.0, 0.0, -0.5]))


def test_translational_acceleration_includes_coriolis_like_term() -> None:
    """A rotating body with nonzero velocity has -omega x V even with zero net force."""
    dv = translational_acceleration(
        velocity_body=np.array([100.0, 0.0, 0.0]),
        angular_velocity_body=np.array([0.0, 0.0, 1.0]),  # yaw rate
        force_body=np.zeros(3),
        mass=1000.0,
    )
    expected = -np.cross(np.array([0.0, 0.0, 1.0]), np.array([100.0, 0.0, 0.0]))
    assert np.allclose(dv, expected)


def test_translational_acceleration_rejects_nonpositive_mass() -> None:
    with pytest.raises(InvalidFlightDynamicsInputError):
        translational_acceleration(np.zeros(3), np.zeros(3), np.zeros(3), mass=0)


def test_translational_acceleration_rejects_bad_shapes() -> None:
    with pytest.raises(InvalidFlightDynamicsInputError):
        translational_acceleration(np.zeros(2), np.zeros(3), np.zeros(3), mass=1.0)


def test_rotational_acceleration_matches_simple_axis_case() -> None:
    domega = rotational_acceleration(
        angular_velocity_body=np.zeros(3),
        moment_body=np.array([0.0, 100.0, 0.0]),
        inertia=np.array([1500.0, 2000.0, 3000.0]),
    )
    assert np.allclose(domega, np.array([0.0, 100.0 / 2000.0, 0.0]))


def test_rotational_acceleration_matches_scalar_euler_equations() -> None:
    """For diagonal inertia, the general matrix form must match the classic scalar
    Euler equations: p_dot = (Mx + (Iyy-Izz)qr)/Ixx, etc."""
    ixx, iyy, izz = 1500.0, 2000.0, 3000.0
    p, q, r = 0.5, -0.3, 0.2
    mx, my, mz = 50.0, -20.0, 10.0
    domega = rotational_acceleration(
        angular_velocity_body=np.array([p, q, r]),
        moment_body=np.array([mx, my, mz]),
        inertia=np.array([ixx, iyy, izz]),
    )
    expected_p_dot = (mx + (iyy - izz) * q * r) / ixx
    expected_q_dot = (my + (izz - ixx) * p * r) / iyy
    expected_r_dot = (mz + (ixx - iyy) * p * q) / izz
    assert math.isclose(domega[0], expected_p_dot, rel_tol=1e-9)
    assert math.isclose(domega[1], expected_q_dot, rel_tol=1e-9)
    assert math.isclose(domega[2], expected_r_dot, rel_tol=1e-9)


def test_rotational_acceleration_accepts_full_inertia_matrix() -> None:
    inertia_diag = np.array([1500.0, 2000.0, 3000.0])
    inertia_matrix = np.diag(inertia_diag)
    domega_vec = rotational_acceleration(
        np.array([0.1, 0.2, 0.3]), np.array([1.0, 2.0, 3.0]), inertia_diag
    )
    domega_mat = rotational_acceleration(
        np.array([0.1, 0.2, 0.3]), np.array([1.0, 2.0, 3.0]), inertia_matrix
    )
    assert np.allclose(domega_vec, domega_mat)


def test_rotational_acceleration_rejects_bad_inertia_shape() -> None:
    with pytest.raises(InvalidFlightDynamicsInputError):
        rotational_acceleration(np.zeros(3), np.zeros(3), inertia=np.zeros(4))


def test_gravity_body_frame_identity_dcm_points_down() -> None:
    g_body = gravity_body_frame(np.eye(3))
    assert np.allclose(g_body, np.array([0.0, 0.0, G0]))


def test_gravity_body_frame_inverted_aircraft_points_up() -> None:
    """An aircraft rolled 180 degrees should feel gravity pointing toward its belly (-Z body)."""
    dcm = euler_to_dcm(math.pi, 0.0, 0.0)
    g_body = gravity_body_frame(dcm)
    assert g_body[2] < 0


def test_gravity_body_frame_rejects_bad_shape() -> None:
    with pytest.raises(InvalidFlightDynamicsInputError):
        gravity_body_frame(np.eye(2))


def test_position_derivative_identity_dcm_passthrough() -> None:
    v = np.array([100.0, 5.0, -2.0])
    assert np.allclose(position_derivative(np.eye(3), v), v)


def test_position_derivative_rotated_frame() -> None:
    """A pure yaw of 90 degrees should map body +x velocity to inertial +y."""
    dcm = euler_to_dcm(0.0, 0.0, math.pi / 2)
    v_body = np.array([100.0, 0.0, 0.0])
    v_inertial = position_derivative(dcm, v_body)
    assert math.isclose(v_inertial[0], 0.0, abs_tol=1e-9)
    assert math.isclose(v_inertial[1], 100.0, abs_tol=1e-9)


def test_position_derivative_rejects_bad_shapes() -> None:
    with pytest.raises(InvalidFlightDynamicsInputError):
        position_derivative(np.eye(2), np.zeros(3))
