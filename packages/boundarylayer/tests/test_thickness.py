"""Validate boundary-layer thickness/skin-friction relations."""

from __future__ import annotations

import math

import pytest
from boundarylayer.exceptions import InvalidReynoldsNumberError
from boundarylayer.thickness import (
    laminar_local_skin_friction,
    laminar_thickness,
    turbulent_local_skin_friction,
    turbulent_thickness,
)


def test_laminar_thickness_formula() -> None:
    assert math.isclose(laminar_thickness(x=1.0, reynolds_x=1e6), 0.005, rel_tol=1e-9)


def test_turbulent_thickness_formula() -> None:
    expected = 0.37 * 1.0 / 1e7**0.2
    assert math.isclose(turbulent_thickness(x=1.0, reynolds_x=1e7), expected, rel_tol=1e-9)


def test_turbulent_layer_thicker_than_laminar_at_same_reynolds() -> None:
    """At a matched Reynolds number, turbulent BL is thicker than laminar
    (more momentum mixing across the layer)."""
    re = 5e5
    assert turbulent_thickness(1.0, re) > laminar_thickness(1.0, re)


def test_boundary_layer_grows_with_distance() -> None:
    """delta increases monotonically with x for a fixed unit Reynolds number per meter."""
    unit_re_per_m = 2e6  # rho*U/mu, so Re_x = unit_re_per_m * x
    thicknesses = [laminar_thickness(x, unit_re_per_m * x) for x in (0.5, 1.0, 2.0, 4.0)]
    assert thicknesses == sorted(thicknesses)


def test_laminar_skin_friction_matches_formula() -> None:
    re = 1e6
    assert math.isclose(laminar_local_skin_friction(re), 0.664 / re**0.5, rel_tol=1e-9)


def test_turbulent_skin_friction_matches_formula() -> None:
    re = 1e7
    assert math.isclose(turbulent_local_skin_friction(re), 0.0592 / re**0.2, rel_tol=1e-9)


@pytest.mark.parametrize("bad_re", [0, -1.0])
def test_functions_reject_nonpositive_reynolds(bad_re: float) -> None:
    with pytest.raises(InvalidReynoldsNumberError):
        laminar_thickness(1.0, bad_re)
    with pytest.raises(InvalidReynoldsNumberError):
        turbulent_thickness(1.0, bad_re)
    with pytest.raises(InvalidReynoldsNumberError):
        laminar_local_skin_friction(bad_re)
    with pytest.raises(InvalidReynoldsNumberError):
        turbulent_local_skin_friction(bad_re)
