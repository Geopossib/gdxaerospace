"""Validate fixed-wing UAV sizing relations."""

from __future__ import annotations

import math

import pytest
from uavpy.exceptions import InvalidUAVInputError
from uavpy.fixed_wing import stall_speed, thrust_to_weight_ratio, wing_loading


def test_wing_loading_matches_formula() -> None:
    assert math.isclose(wing_loading(98.1, 0.6), 98.1 / 0.6, rel_tol=1e-9)


def test_wing_loading_rejects_nonpositive_inputs() -> None:
    with pytest.raises(InvalidUAVInputError):
        wing_loading(0, 0.6)
    with pytest.raises(InvalidUAVInputError):
        wing_loading(98.1, 0)


def test_thrust_to_weight_ratio_matches_formula() -> None:
    assert math.isclose(thrust_to_weight_ratio(30.0, 98.1), 30.0 / 98.1, rel_tol=1e-9)


def test_thrust_to_weight_ratio_rejects_nonpositive_inputs() -> None:
    with pytest.raises(InvalidUAVInputError):
        thrust_to_weight_ratio(0, 98.1)
    with pytest.raises(InvalidUAVInputError):
        thrust_to_weight_ratio(30.0, 0)


def test_stall_speed_matches_formula() -> None:
    w, s, cl_max, rho = 98.1, 0.6, 1.2, 1.225
    expected = math.sqrt(2 * w / (rho * s * cl_max))
    assert math.isclose(stall_speed(w, s, cl_max, rho), expected, rel_tol=1e-9)


def test_stall_speed_higher_wing_loading_gives_higher_stall_speed() -> None:
    low = stall_speed(weight=50.0, wing_area=0.6, max_lift_coefficient=1.2)
    high = stall_speed(weight=100.0, wing_area=0.6, max_lift_coefficient=1.2)
    assert high > low


def test_stall_speed_higher_cl_max_gives_lower_stall_speed() -> None:
    """Better high-lift devices (higher CL_max) reduce stall speed."""
    low_cl = stall_speed(weight=98.1, wing_area=0.6, max_lift_coefficient=1.2)
    high_cl = stall_speed(weight=98.1, wing_area=0.6, max_lift_coefficient=2.0)
    assert high_cl < low_cl


def test_stall_speed_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidUAVInputError):
        stall_speed(0, 0.6, 1.2)
    with pytest.raises(InvalidUAVInputError):
        stall_speed(98.1, 0, 1.2)
    with pytest.raises(InvalidUAVInputError):
        stall_speed(98.1, 0.6, 0)
    with pytest.raises(InvalidUAVInputError):
        stall_speed(98.1, 0.6, 1.2, air_density=0)
