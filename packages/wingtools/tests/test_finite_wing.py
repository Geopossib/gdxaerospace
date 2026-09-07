"""Validate finite-wing lift-curve-slope, Oswald efficiency, and induced drag."""

from __future__ import annotations

import math

import pytest
from wingtools.exceptions import InvalidWingGeometryError
from wingtools.finite_wing import (
    finite_wing_lift_curve_slope,
    induced_drag_coefficient,
    oswald_efficiency_estimate,
)


def test_finite_wing_slope_less_than_2d_slope() -> None:
    """3D effects always reduce lift-curve slope relative to the 2D airfoil value."""
    a0 = 2 * math.pi
    a3d_helm = finite_wing_lift_curve_slope(a0, aspect_ratio=8.0, model="helmbold")
    a3d_prandtl = finite_wing_lift_curve_slope(a0, aspect_ratio=8.0, model="prandtl")
    assert a3d_helm < a0
    assert a3d_prandtl < a0


def test_finite_wing_slope_matches_prandtl_formula() -> None:
    a0 = 2 * math.pi
    ar = 8.0
    expected = a0 / (1 + a0 / (math.pi * ar))
    assert math.isclose(
        finite_wing_lift_curve_slope(a0, ar, model="prandtl"), expected, rel_tol=1e-9
    )


def test_finite_wing_slope_approaches_2d_as_ar_grows() -> None:
    """As AR -> infinity, the finite-wing slope approaches the 2D value."""
    a0 = 2 * math.pi
    a3d_small = finite_wing_lift_curve_slope(a0, aspect_ratio=6.0)
    a3d_large = finite_wing_lift_curve_slope(a0, aspect_ratio=1000.0)
    assert a3d_large > a3d_small
    assert math.isclose(a3d_large, a0, rel_tol=0.01)


def test_finite_wing_slope_rejects_nonpositive_aspect_ratio() -> None:
    with pytest.raises(InvalidWingGeometryError):
        finite_wing_lift_curve_slope(2 * math.pi, aspect_ratio=0)
    with pytest.raises(InvalidWingGeometryError):
        finite_wing_lift_curve_slope(2 * math.pi, aspect_ratio=-1.0)


def test_finite_wing_slope_rejects_unknown_model() -> None:
    with pytest.raises(InvalidWingGeometryError):
        finite_wing_lift_curve_slope(2 * math.pi, aspect_ratio=8.0, model="bogus")


def test_oswald_efficiency_matches_raymer_formula_unswept() -> None:
    ar = 8.0
    expected = 1.78 * (1 - 0.045 * ar**0.68) - 0.64
    assert math.isclose(oswald_efficiency_estimate(ar), expected, rel_tol=1e-9)


def test_oswald_efficiency_in_typical_range() -> None:
    for ar in (5.0, 8.0, 10.0, 12.0):
        e = oswald_efficiency_estimate(ar)
        assert 0.6 < e < 1.0


def test_oswald_efficiency_rejects_nonpositive_aspect_ratio() -> None:
    with pytest.raises(InvalidWingGeometryError):
        oswald_efficiency_estimate(0)


def test_induced_drag_matches_formula() -> None:
    cl, ar, e = 0.5, 8.0, 0.85
    expected = cl**2 / (math.pi * e * ar)
    assert math.isclose(
        induced_drag_coefficient(cl, ar, oswald_efficiency=e), expected, rel_tol=1e-9
    )


def test_induced_drag_scales_with_cl_squared() -> None:
    ar = 8.0
    cdi_1 = induced_drag_coefficient(0.5, ar)
    cdi_2 = induced_drag_coefficient(1.0, ar)
    assert math.isclose(cdi_2 / cdi_1, 4.0, rel_tol=1e-9)


def test_induced_drag_decreases_with_aspect_ratio() -> None:
    cl = 0.5
    assert induced_drag_coefficient(cl, 12.0) < induced_drag_coefficient(cl, 6.0)


def test_induced_drag_rejects_invalid_efficiency() -> None:
    with pytest.raises(InvalidWingGeometryError):
        induced_drag_coefficient(0.5, 8.0, oswald_efficiency=0)
    with pytest.raises(InvalidWingGeometryError):
        induced_drag_coefficient(0.5, 8.0, oswald_efficiency=1.5)


def test_induced_drag_rejects_nonpositive_aspect_ratio() -> None:
    with pytest.raises(InvalidWingGeometryError):
        induced_drag_coefficient(0.5, 0)
