"""Validate two-body orbital mechanics relations."""

from __future__ import annotations

import math

import numpy as np
import pytest
from orbitpy.constants import EARTH_MU
from orbitpy.elements import cartesian_to_kepler, kepler_to_cartesian
from orbitpy.exceptions import InvalidOrbitError, OrbitSolverConvergenceError
from orbitpy.kepler import (
    circular_velocity,
    eccentric_anomaly_from_true,
    escape_velocity,
    orbital_period,
    solve_kepler_equation,
    true_anomaly_from_eccentric,
    vis_viva_speed,
)
from orbitpy.maneuvers import (
    bielliptic_transfer,
    combined_plane_change_delta_v,
    hohmann_transfer,
    inclination_change_delta_v,
)

# --- Kepler relations ---


def test_orbital_period_matches_formula() -> None:
    a = 6_778_000.0
    expected = 2 * math.pi * math.sqrt(a**3 / EARTH_MU)
    assert math.isclose(orbital_period(a), expected, rel_tol=1e-9)


def test_orbital_period_iss_like_orbit_matches_known_ballpark() -> None:
    """The ISS orbits Earth roughly every ~92-93 minutes."""
    period_min = orbital_period(6_778_000.0) / 60
    assert 90 < period_min < 95


def test_orbital_period_geo_matches_sidereal_day() -> None:
    """A GEO orbit's period should be very close to one sidereal day (~23h56m)."""
    geo_radius = 42_164_000.0
    period_hours = orbital_period(geo_radius) / 3600
    assert math.isclose(period_hours, 23.934, rel_tol=1e-3)


def test_orbital_period_rejects_nonpositive_semi_major_axis() -> None:
    with pytest.raises(InvalidOrbitError):
        orbital_period(0)


def test_circular_velocity_matches_formula() -> None:
    r = 6_778_000.0
    assert math.isclose(circular_velocity(r), math.sqrt(EARTH_MU / r), rel_tol=1e-9)


def test_escape_velocity_is_sqrt2_times_circular_velocity() -> None:
    r = 6_778_000.0
    assert math.isclose(escape_velocity(r), math.sqrt(2) * circular_velocity(r), rel_tol=1e-9)


def test_vis_viva_reduces_to_circular_velocity_when_r_equals_a() -> None:
    r = 7_000_000.0
    assert math.isclose(vis_viva_speed(r, r), circular_velocity(r), rel_tol=1e-9)


def test_solve_kepler_equation_matches_definition() -> None:
    """The solved E must satisfy M = E - e*sin(E) to high precision."""
    m, e = 1.0, 0.1
    big_e = solve_kepler_equation(m, e)
    assert math.isclose(big_e - e * math.sin(big_e), m, abs_tol=1e-10)


def test_solve_kepler_equation_zero_eccentricity_gives_e_equals_m() -> None:
    m = 1.234
    assert math.isclose(solve_kepler_equation(m, 0.0), m, rel_tol=1e-9)


def test_solve_kepler_equation_rejects_invalid_eccentricity() -> None:
    with pytest.raises(InvalidOrbitError):
        solve_kepler_equation(1.0, 1.0)
    with pytest.raises(InvalidOrbitError):
        solve_kepler_equation(1.0, -0.1)


def test_solve_kepler_equation_raises_on_nonconvergence() -> None:
    with pytest.raises(OrbitSolverConvergenceError):
        solve_kepler_equation(1.0, 0.5, max_iterations=0)


def test_true_and_eccentric_anomaly_round_trip() -> None:
    for e_anomaly in (0.1, 1.0, 2.0, 3.0):
        for e in (0.0, 0.2, 0.5, 0.9):
            nu = true_anomaly_from_eccentric(e_anomaly, e)
            recovered = eccentric_anomaly_from_true(nu, e)
            assert math.isclose(recovered, e_anomaly, abs_tol=1e-9)


def test_true_anomaly_equals_eccentric_anomaly_for_circular_orbit() -> None:
    assert math.isclose(true_anomaly_from_eccentric(1.5, 0.0), 1.5, abs_tol=1e-9)


# --- Element/state-vector conversions ---


def test_kepler_to_cartesian_circular_equatorial_speed_matches_circular_velocity() -> None:
    a = 7_000_000.0
    r, v = kepler_to_cartesian(a, 0.0, 0.0, 0.0, 0.0, 0.0)
    assert math.isclose(float(np.linalg.norm(r)), a, rel_tol=1e-9)
    assert math.isclose(float(np.linalg.norm(v)), circular_velocity(a), rel_tol=1e-6)


@pytest.mark.parametrize(
    "a,e,i,raan,argp,nu",
    [
        (7_000_000.0, 0.0, 0.0, 0.0, 0.0, 0.5),
        (7_000_000.0, 0.0, math.radians(51.6), math.radians(30), 0.0, 1.2),
        (8_000_000.0, 0.3, math.radians(28.5), math.radians(60), math.radians(40), 2.0),
        (9_000_000.0, 0.2, 0.0, 0.0, math.radians(80), 1.0),
        (42_164_000.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        (8_500_000.0, 0.1, math.radians(90), math.radians(10), math.radians(200), 3.0),
    ],
)
def test_kepler_cartesian_round_trip(
    a: float, e: float, i: float, raan: float, argp: float, nu: float
) -> None:
    r, v = kepler_to_cartesian(a, e, i, raan, argp, nu)
    a2, e2, i2, raan2, argp2, nu2 = cartesian_to_kepler(r, v)
    assert math.isclose(a2, a, rel_tol=1e-6)
    assert math.isclose(e2, e, abs_tol=1e-6)
    assert math.isclose(i2, i, abs_tol=1e-6)
    assert math.isclose(raan2, raan % (2 * math.pi), abs_tol=1e-6)
    assert math.isclose(argp2, argp % (2 * math.pi), abs_tol=1e-6)
    assert math.isclose(nu2, nu % (2 * math.pi), abs_tol=1e-6)


def test_kepler_to_cartesian_rejects_invalid_elements() -> None:
    with pytest.raises(InvalidOrbitError):
        kepler_to_cartesian(0, 0.0, 0.0, 0.0, 0.0, 0.0)
    with pytest.raises(InvalidOrbitError):
        kepler_to_cartesian(7_000_000.0, 1.0, 0.0, 0.0, 0.0, 0.0)
    with pytest.raises(InvalidOrbitError):
        kepler_to_cartesian(7_000_000.0, 0.0, math.pi + 0.1, 0.0, 0.0, 0.0)


def test_cartesian_to_kepler_rejects_hyperbolic_orbit() -> None:
    r = np.array([7_000_000.0, 0.0, 0.0])
    v = np.array([0.0, 15000.0, 0.0])  # far exceeds escape velocity
    with pytest.raises(InvalidOrbitError):
        cartesian_to_kepler(r, v)


def test_cartesian_to_kepler_rejects_bad_shapes() -> None:
    with pytest.raises(InvalidOrbitError):
        cartesian_to_kepler(np.array([1.0, 0.0]), np.array([0.0, 1.0, 0.0]))


# --- Maneuvers ---


def test_hohmann_transfer_leo_to_geo_matches_known_ballpark() -> None:
    """LEO-to-GEO Hohmann transfer total delta-v is commonly cited as ~3.9 km/s."""
    result = hohmann_transfer(r1=6_678_000.0, r2=42_164_000.0)
    assert 3800 < result.total_delta_v < 4000


def test_hohmann_transfer_symmetric_under_swap() -> None:
    """Transferring r1->r2 then r2->r1 should need the same total delta-v (by symmetry
    of the underlying ellipse, though the individual burns swap roles)."""
    forward = hohmann_transfer(6_678_000.0, 42_164_000.0)
    backward = hohmann_transfer(42_164_000.0, 6_678_000.0)
    assert math.isclose(forward.total_delta_v, backward.total_delta_v, rel_tol=1e-9)


def test_hohmann_transfer_same_radius_gives_zero_delta_v() -> None:
    result = hohmann_transfer(7_000_000.0, 7_000_000.0)
    assert math.isclose(result.total_delta_v, 0.0, abs_tol=1e-9)


def test_hohmann_transfer_rejects_nonpositive_radii() -> None:
    with pytest.raises(InvalidOrbitError):
        hohmann_transfer(0, 42_164_000.0)


def test_bielliptic_beats_hohmann_for_large_radius_ratio() -> None:
    """Per Vallado, bi-elliptic beats Hohmann when r2/r1 is large (roughly > 11.94)."""
    r1, r2 = 6_678_000.0, 200_000_000.0
    hohmann = hohmann_transfer(r1, r2)
    bielliptic = bielliptic_transfer(r1, r2, r_intermediate=300_000_000.0)
    assert bielliptic.total_delta_v < hohmann.total_delta_v


def test_bielliptic_worse_than_hohmann_for_small_radius_ratio() -> None:
    """For a small ratio, bi-elliptic's extra burn should cost more than it saves."""
    r1, r2 = 6_678_000.0, 42_164_000.0
    hohmann = hohmann_transfer(r1, r2)
    bielliptic = bielliptic_transfer(r1, r2, r_intermediate=100_000_000.0)
    assert bielliptic.total_delta_v > hohmann.total_delta_v


def test_bielliptic_rejects_intermediate_radius_not_exceeding_both() -> None:
    with pytest.raises(InvalidOrbitError):
        bielliptic_transfer(6_678_000.0, 42_164_000.0, r_intermediate=10_000_000.0)


def test_inclination_change_zero_for_zero_delta_inclination() -> None:
    assert inclination_change_delta_v(7668.6, 0.0) == 0.0


def test_inclination_change_matches_formula() -> None:
    v, di = 7668.6, 0.5
    expected = 2 * v * math.sin(di / 2)
    assert math.isclose(inclination_change_delta_v(v, di), expected, rel_tol=1e-9)


def test_inclination_change_rejects_nonpositive_velocity() -> None:
    with pytest.raises(InvalidOrbitError):
        inclination_change_delta_v(0, 0.5)


def test_combined_plane_change_reduces_to_speed_difference_at_zero_inclination() -> None:
    v1, v2 = 10000.0, 8000.0
    assert math.isclose(
        combined_plane_change_delta_v(v1, v2, 0.0), abs(v1 - v2), rel_tol=1e-9
    )


def test_combined_plane_change_matches_law_of_cosines() -> None:
    v1, v2, di = 10000.0, 1467.6, math.radians(28.5)
    expected = math.sqrt(v1**2 + v2**2 - 2 * v1 * v2 * math.cos(di))
    assert math.isclose(combined_plane_change_delta_v(v1, v2, di), expected, rel_tol=1e-9)


def test_combined_plane_change_rejects_nonpositive_speeds() -> None:
    with pytest.raises(InvalidOrbitError):
        combined_plane_change_delta_v(0, 1000.0, 0.1)
