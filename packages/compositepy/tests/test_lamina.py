"""Validate orthotropic lamina stiffness and axis transformation."""

from __future__ import annotations

import math

import pytest
from compositepy.exceptions import InvalidLaminaError
from compositepy.lamina import reduced_stiffness, transform_stiffness

_E1, _E2, _NU12, _G12 = 181e9, 10.3e9, 0.28, 7.17e9  # T300/5208, Jones Table 2-2


def test_reduced_stiffness_matches_formula() -> None:
    q = reduced_stiffness(_E1, _E2, _NU12, _G12)
    nu21 = _NU12 * _E2 / _E1
    denom = 1 - _NU12 * nu21
    assert math.isclose(q.q11, _E1 / denom, rel_tol=1e-9)
    assert math.isclose(q.q22, _E2 / denom, rel_tol=1e-9)
    assert math.isclose(q.q12, _NU12 * _E2 / denom, rel_tol=1e-9)
    assert math.isclose(q.q66, _G12, rel_tol=1e-9)


def test_reduced_stiffness_q11_much_greater_than_q22() -> None:
    """Fiber-direction stiffness should dominate for a typical unidirectional composite."""
    q = reduced_stiffness(_E1, _E2, _NU12, _G12)
    assert q.q11 > 10 * q.q22


def test_reduced_stiffness_symmetric_relation() -> None:
    """Q12 should equal nu21*Q11 as well as nu12*Q22 (reciprocal Poisson relation)."""
    q = reduced_stiffness(_E1, _E2, _NU12, _G12)
    nu21 = _NU12 * _E2 / _E1
    assert math.isclose(q.q12, nu21 * q.q11, rel_tol=1e-6)


def test_reduced_stiffness_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidLaminaError):
        reduced_stiffness(0, _E2, _NU12, _G12)
    with pytest.raises(InvalidLaminaError):
        reduced_stiffness(_E1, 0, _NU12, _G12)
    with pytest.raises(InvalidLaminaError):
        reduced_stiffness(_E1, _E2, 1.5, _G12)
    with pytest.raises(InvalidLaminaError):
        reduced_stiffness(_E1, _E2, _NU12, 0)


def test_transform_stiffness_zero_angle_matches_material_axes() -> None:
    q = reduced_stiffness(_E1, _E2, _NU12, _G12)
    q_bar = transform_stiffness(q, 0.0)
    assert math.isclose(q_bar.q11, q.q11, rel_tol=1e-9)
    assert math.isclose(q_bar.q22, q.q22, rel_tol=1e-9)
    assert math.isclose(q_bar.q12, q.q12, rel_tol=1e-9)
    assert math.isclose(q_bar.q66, q.q66, rel_tol=1e-9)
    assert math.isclose(q_bar.q16, 0.0, abs_tol=1e-3)
    assert math.isclose(q_bar.q26, 0.0, abs_tol=1e-3)


def test_transform_stiffness_90_degrees_swaps_q11_and_q22() -> None:
    q = reduced_stiffness(_E1, _E2, _NU12, _G12)
    q_bar = transform_stiffness(q, math.radians(90.0))
    assert math.isclose(q_bar.q11, q.q22, rel_tol=1e-6)
    assert math.isclose(q_bar.q22, q.q11, rel_tol=1e-6)
    assert math.isclose(q_bar.q12, q.q12, rel_tol=1e-6)


def test_transform_stiffness_180_degrees_matches_zero_degrees() -> None:
    """A fiber direction is a line, not a vector -- 180 deg rotation is physically
    identical to 0 deg."""
    q = reduced_stiffness(_E1, _E2, _NU12, _G12)
    q_bar_0 = transform_stiffness(q, 0.0)
    q_bar_180 = transform_stiffness(q, math.pi)
    assert math.isclose(q_bar_0.q11, q_bar_180.q11, rel_tol=1e-6)
    assert math.isclose(q_bar_0.q22, q_bar_180.q22, rel_tol=1e-6)


def test_transform_stiffness_45_degrees_symmetric_q11_q22() -> None:
    """At 45 degrees, Q11_bar and Q22_bar are equal by symmetry of the transform."""
    q = reduced_stiffness(_E1, _E2, _NU12, _G12)
    q_bar = transform_stiffness(q, math.radians(45.0))
    assert math.isclose(q_bar.q11, q_bar.q22, rel_tol=1e-9)
    assert math.isclose(q_bar.q16, q_bar.q26, rel_tol=1e-9)
