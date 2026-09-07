"""Validate isentropic relations against Anderson's Appendix A tables."""

from __future__ import annotations

import math

import pytest
from aerocalc.exceptions import InvalidMachNumberError
from compressibleflow.isentropic import (
    area_mach_ratio,
    stagnation_density_ratio,
    stagnation_pressure_ratio,
    stagnation_temperature_ratio,
)

# (Mach, T0/T, p0/p, rho0/rho, A/A*) from Anderson, Fundamentals of Aerodynamics,
# Appendix A (Isentropic Flow Properties, gamma=1.4).
_REFERENCE_TABLE = [
    (0.5, 1.0500, 1.1862, 1.1297, 1.3398),
    (1.0, 1.2000, 1.8929, 1.5774, 1.0000),
    (2.0, 1.8000, 7.8244, 4.3469, 1.6875),
    (3.0, 2.8000, 36.7327, 13.1188, 4.2346),
]


@pytest.mark.parametrize("mach,t_ratio,p_ratio,rho_ratio,a_ratio", _REFERENCE_TABLE)
def test_isentropic_ratios_match_anderson_table(
    mach: float, t_ratio: float, p_ratio: float, rho_ratio: float, a_ratio: float
) -> None:
    assert math.isclose(stagnation_temperature_ratio(mach), t_ratio, rel_tol=1e-4)
    assert math.isclose(stagnation_pressure_ratio(mach), p_ratio, rel_tol=1e-3)
    assert math.isclose(stagnation_density_ratio(mach), rho_ratio, rel_tol=1e-3)
    if mach > 0:
        assert math.isclose(area_mach_ratio(mach), a_ratio, rel_tol=1e-3)


def test_sonic_area_ratio_is_unity() -> None:
    """At M=1, A/A* = 1 by definition (the throat)."""
    assert math.isclose(area_mach_ratio(1.0), 1.0, rel_tol=1e-9)


def test_all_ratios_equal_one_at_zero_mach() -> None:
    assert stagnation_temperature_ratio(0.0) == 1.0
    assert stagnation_pressure_ratio(0.0) == 1.0
    assert stagnation_density_ratio(0.0) == 1.0


def test_negative_mach_raises() -> None:
    with pytest.raises(InvalidMachNumberError):
        stagnation_temperature_ratio(-1.0)


def test_area_mach_ratio_rejects_zero_mach() -> None:
    with pytest.raises(InvalidMachNumberError):
        area_mach_ratio(0.0)


def test_helium_gamma_gives_different_ratio_than_air() -> None:
    """Sanity check that the gamma parameter actually changes the result."""
    air_ratio = stagnation_pressure_ratio(2.0, gamma=1.4)
    helium_ratio = stagnation_pressure_ratio(2.0, gamma=1.667)
    assert air_ratio != helium_ratio
