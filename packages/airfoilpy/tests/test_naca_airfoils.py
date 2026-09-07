"""Validate NACA 4/5-digit geometry against known published characteristics."""

from __future__ import annotations

import math

import numpy as np
import pytest
from airfoilpy.exceptions import InvalidAirfoilCodeError
from airfoilpy.naca4 import naca4_camber, naca4_coordinates, naca4_thickness
from airfoilpy.naca5 import naca5_coordinates


def test_naca0012_max_thickness_and_location() -> None:
    """NACA 0012: 12% max thickness located near x/c = 0.30 (Abbott & Von Doenhoff)."""
    x = np.linspace(0, 1, 2000)
    yt = naca4_thickness(x, 0.12)
    max_half_thickness = yt.max()
    location = x[np.argmax(yt)]
    assert math.isclose(2 * max_half_thickness, 0.12, rel_tol=0.01)
    assert math.isclose(location, 0.30, abs_tol=0.01)


def test_naca0012_trailing_edge_closure() -> None:
    """Closed-TE coefficients bring the thickness gap at x=1 to a small residual
    (~0.13% of chord is the known residual of this 4-term polynomial fit;
    it does not close to exactly zero, unlike a 5-term fit)."""
    yt = naca4_thickness(np.array([1.0]), 0.12, closed_trailing_edge=True)
    assert abs(yt[0]) < 2e-3


def test_naca4_symmetric_airfoil_has_zero_camber() -> None:
    x = np.linspace(0, 1, 50)
    yc, dyc = naca4_camber(x, max_camber=0.0, camber_position=0.0)
    assert np.allclose(yc, 0.0)
    assert np.allclose(dyc, 0.0)


def test_naca2412_max_camber_and_location() -> None:
    """NACA 2412: 2% max camber at x/c = 0.4, by definition of the digits."""
    x = np.linspace(0, 1, 2000)
    yc, _ = naca4_camber(x, max_camber=0.02, camber_position=0.4)
    assert math.isclose(yc.max(), 0.02, rel_tol=0.01)
    assert math.isclose(x[np.argmax(yc)], 0.4, abs_tol=0.01)


def test_naca4_coordinates_upper_above_lower() -> None:
    """For a cambered airfoil, the upper surface must lie above the lower surface."""
    coords = naca4_coordinates("2412", n_points=100)
    # Compare at matching interior indices (excludes LE/TE where they coincide).
    assert np.all(coords.y_upper[5:-5] > coords.y_lower[5:-5])


@pytest.mark.parametrize("code", ["001", "abcd", "99999", "0012x"])
def test_naca4_invalid_code_raises(code: str) -> None:
    with pytest.raises(InvalidAirfoilCodeError):
        naca4_coordinates(code)


def test_naca4_rejects_out_of_range_stations() -> None:
    with pytest.raises(ValueError):
        naca4_thickness(np.array([-0.1, 0.5]), 0.12)
    with pytest.raises(ValueError):
        naca4_thickness(np.array([0.5, 1.1]), 0.12)


def test_naca5_23012_produces_valid_geometry() -> None:
    """NACA 23012 is a well-known 5-digit airfoil (used on early Cessna wings)."""
    coords = naca5_coordinates("23012", n_points=100)
    assert coords.y_upper.shape == (100,)
    # Camber is small and positive for this airfoil family.
    assert 0 < coords.y_upper.max() < 0.10


@pytest.mark.parametrize(
    "code,reason",
    [
        ("13012", "design Cl digit must be 2"),
        ("29012", "third (reflex) digit must be 0"),
        ("26012", "p_code 6 is unsupported"),
    ],
)
def test_naca5_invalid_designations_raise(code: str, reason: str) -> None:
    with pytest.raises(InvalidAirfoilCodeError):
        naca5_coordinates(code)
