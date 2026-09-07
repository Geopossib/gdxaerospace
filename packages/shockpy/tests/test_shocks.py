"""Validate shock/expansion relations against Anderson's Appendix B/C tables."""

from __future__ import annotations

import math

import pytest
from aerocalc.exceptions import InvalidMachNumberError
from shockpy.exceptions import DetachedShockError
from shockpy.normal_shock import normal_shock
from shockpy.oblique_shock import oblique_shock, theta_from_beta
from shockpy.prandtl_meyer import expansion_fan, mach_from_prandtl_meyer_angle, prandtl_meyer_angle

# --- Normal shock: (M1, M2, p2/p1, T2/T1, rho2/rho1, p02/p01) from Anderson Appendix B ---
_NORMAL_SHOCK_TABLE = [
    (1.5, 0.7011, 2.4583, 1.3202, 1.8621, 0.9298),
    (2.0, 0.5774, 4.5000, 1.6875, 2.6667, 0.7209),
    (3.0, 0.4752, 10.3333, 2.6790, 3.8571, 0.3283),
]


@pytest.mark.parametrize("m1,m2,p_ratio,t_ratio,rho_ratio,p0_ratio", _NORMAL_SHOCK_TABLE)
def test_normal_shock_matches_anderson_table(
    m1: float, m2: float, p_ratio: float, t_ratio: float, rho_ratio: float, p0_ratio: float
) -> None:
    result = normal_shock(m1)
    assert math.isclose(result.mach_downstream, m2, rel_tol=1e-3)
    assert math.isclose(result.pressure_ratio, p_ratio, rel_tol=1e-3)
    assert math.isclose(result.temperature_ratio, t_ratio, rel_tol=1e-3)
    assert math.isclose(result.density_ratio, rho_ratio, rel_tol=1e-3)
    assert math.isclose(result.stagnation_pressure_ratio, p0_ratio, rel_tol=1e-3)


def test_normal_shock_downstream_is_always_subsonic() -> None:
    for m1 in (1.1, 1.5, 2.0, 3.0, 5.0):
        assert normal_shock(m1).mach_downstream < 1.0


def test_normal_shock_rejects_subsonic_upstream() -> None:
    with pytest.raises(InvalidMachNumberError):
        normal_shock(0.8)
    with pytest.raises(InvalidMachNumberError):
        normal_shock(1.0)


def test_normal_shock_entropy_increases() -> None:
    """Stagnation pressure ratio must be < 1 (entropy increases across a real shock)."""
    for m1 in (1.2, 2.0, 4.0):
        assert normal_shock(m1).stagnation_pressure_ratio < 1.0


def test_oblique_shock_weak_solution_matches_known_chart_value() -> None:
    """M1=2, theta=10deg -> beta ~= 39.3deg (classic Anderson worked example)."""
    result = oblique_shock(2.0, math.radians(10.0))
    assert math.isclose(math.degrees(result.shock_angle), 39.3, abs_tol=0.2)
    assert math.isclose(result.pressure_ratio, 1.707, rel_tol=1e-2)


def test_oblique_shock_weak_angle_less_than_strong_angle() -> None:
    weak = oblique_shock(2.5, math.radians(10.0), weak=True)
    strong = oblique_shock(2.5, math.radians(10.0), weak=False)
    assert weak.shock_angle < strong.shock_angle


def test_oblique_shock_zero_deflection_approaches_mach_wave() -> None:
    """As deflection -> 0, beta -> Mach angle mu = asin(1/M1)."""
    mach1 = 2.0
    small_theta = math.radians(0.5)
    result = oblique_shock(mach1, small_theta)
    mach_angle = math.asin(1 / mach1)
    assert abs(result.shock_angle - mach_angle) < math.radians(3)


def test_oblique_shock_detaches_beyond_max_deflection() -> None:
    """M1=2 has a known theta_max of ~22.97 deg; 40 deg must detach."""
    with pytest.raises(DetachedShockError):
        oblique_shock(2.0, math.radians(40.0))


def test_theta_from_beta_zero_at_mach_angle() -> None:
    """At beta = mu (the Mach angle), the shock has zero strength: theta = 0."""
    mach1 = 3.0
    mu = math.asin(1 / mach1)
    theta = theta_from_beta(mach1, mu)
    assert abs(theta) < 1e-6


# --- Prandtl-Meyer: (M, nu[deg]) from Anderson Appendix C ---
_PM_TABLE = [
    (1.0, 0.0),
    (1.5, 11.91),
    (2.0, 26.38),
    (3.0, 49.76),
]


@pytest.mark.parametrize("mach,nu_deg", _PM_TABLE)
def test_prandtl_meyer_matches_anderson_table(mach: float, nu_deg: float) -> None:
    nu = prandtl_meyer_angle(mach)
    assert math.isclose(math.degrees(nu), nu_deg, abs_tol=0.05)


def test_prandtl_meyer_inverse_round_trip() -> None:
    for mach in (1.2, 1.8, 2.5, 4.0):
        nu = prandtl_meyer_angle(mach)
        recovered = mach_from_prandtl_meyer_angle(nu)
        assert math.isclose(recovered, mach, rel_tol=1e-5)


def test_prandtl_meyer_rejects_subsonic() -> None:
    with pytest.raises(InvalidMachNumberError):
        prandtl_meyer_angle(0.9)


def test_expansion_fan_accelerates_flow_isentropically() -> None:
    """A convex-corner expansion always accelerates the flow with no stagnation loss."""
    mach2, p0_ratio = expansion_fan(2.0, math.radians(10.0))
    assert mach2 > 2.0
    assert p0_ratio == 1.0
    assert math.isclose(mach2, 2.385, rel_tol=1e-3)
