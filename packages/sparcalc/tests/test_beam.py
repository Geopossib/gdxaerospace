"""Validate cantilever beam deflection and shear-flow formulas."""

from __future__ import annotations

import math

import pytest
from sparcalc.beam import (
    cantilever_tip_deflection_distributed_load,
    cantilever_tip_deflection_point_load,
    cantilever_tip_slope_point_load,
    shear_flow,
)
from sparcalc.exceptions import InvalidSparInputError


def test_point_load_deflection_matches_formula() -> None:
    p, length, e, i = 1000.0, 2.0, 71.7e9, 1e-6
    expected = p * length**3 / (3 * e * i)
    assert math.isclose(
        cantilever_tip_deflection_point_load(p, length, e, i), expected, rel_tol=1e-9
    )


def test_point_load_deflection_scales_with_cube_of_length() -> None:
    p, e, i = 1000.0, 71.7e9, 1e-6
    short = cantilever_tip_deflection_point_load(p, 1.0, e, i)
    long_ = cantilever_tip_deflection_point_load(p, 2.0, e, i)
    assert math.isclose(long_ / short, 8.0, rel_tol=1e-9)  # 2^3 = 8


def test_point_load_deflection_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidSparInputError):
        cantilever_tip_deflection_point_load(1000.0, 0, 71.7e9, 1e-6)
    with pytest.raises(InvalidSparInputError):
        cantilever_tip_deflection_point_load(1000.0, 2.0, 0, 1e-6)
    with pytest.raises(InvalidSparInputError):
        cantilever_tip_deflection_point_load(1000.0, 2.0, 71.7e9, 0)


def test_distributed_load_deflection_matches_formula() -> None:
    w, length, e, i = 500.0, 2.0, 71.7e9, 1e-6
    expected = w * length**4 / (8 * e * i)
    assert math.isclose(
        cantilever_tip_deflection_distributed_load(w, length, e, i), expected, rel_tol=1e-9
    )


def test_distributed_load_deflection_scales_with_fourth_power_of_length() -> None:
    w, e, i = 500.0, 71.7e9, 1e-6
    short = cantilever_tip_deflection_distributed_load(w, 1.0, e, i)
    long_ = cantilever_tip_deflection_distributed_load(w, 2.0, e, i)
    assert math.isclose(long_ / short, 16.0, rel_tol=1e-9)  # 2^4 = 16


def test_stiffer_beam_deflects_less() -> None:
    p, length, e = 1000.0, 2.0, 71.7e9
    stiff = cantilever_tip_deflection_point_load(p, length, e, 2e-6)
    flexible = cantilever_tip_deflection_point_load(p, length, e, 1e-6)
    assert stiff < flexible


def test_tip_slope_matches_formula() -> None:
    p, length, e, i = 1000.0, 2.0, 71.7e9, 1e-6
    expected = p * length**2 / (2 * e * i)
    assert math.isclose(cantilever_tip_slope_point_load(p, length, e, i), expected, rel_tol=1e-9)


def test_tip_slope_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidSparInputError):
        cantilever_tip_slope_point_load(1000.0, -1.0, 71.7e9, 1e-6)


def test_shear_flow_matches_formula() -> None:
    v, q, i = 5000.0, 1.5e-4, 8.55e-7
    assert math.isclose(shear_flow(v, q, i), v * q / i, rel_tol=1e-9)


def test_shear_flow_zero_at_extreme_fiber() -> None:
    """At the outermost fiber, the first moment of area beyond that point is zero."""
    assert shear_flow(5000.0, 0.0, 8.55e-7) == 0.0


def test_shear_flow_rejects_nonpositive_moment_of_inertia() -> None:
    with pytest.raises(InvalidSparInputError):
        shear_flow(5000.0, 1.5e-4, 0)
