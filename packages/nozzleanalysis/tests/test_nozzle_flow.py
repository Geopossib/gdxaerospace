"""Validate isentropic nozzle-flow relations."""

from __future__ import annotations

import math

import pytest
from compressibleflow.isentropic import area_mach_ratio
from nozzleanalysis.exceptions import InvalidNozzleInputError
from nozzleanalysis.nozzle_flow import (
    choked_mass_flow,
    exit_mach_from_area_ratio,
    nozzle_exit_conditions,
)


def test_choked_mass_flow_matches_hand_calculation() -> None:
    g, r, pc, tc, at = 1.22, 287.05287, 7e6, 3500.0, 0.01
    expected = at * pc * math.sqrt(g / (r * tc)) * (2 / (g + 1)) ** ((g + 1) / (2 * (g - 1)))
    actual = choked_mass_flow(pc, tc, at, gamma=g, specific_gas_constant=r)
    assert math.isclose(actual, expected, rel_tol=1e-9)


def test_choked_mass_flow_scales_linearly_with_throat_area() -> None:
    m1 = choked_mass_flow(7e6, 3500.0, 0.01, gamma=1.22)
    m2 = choked_mass_flow(7e6, 3500.0, 0.02, gamma=1.22)
    assert math.isclose(m2 / m1, 2.0, rel_tol=1e-9)


def test_choked_mass_flow_rejects_nonpositive_inputs() -> None:
    with pytest.raises(InvalidNozzleInputError):
        choked_mass_flow(0, 3500.0, 0.01)
    with pytest.raises(InvalidNozzleInputError):
        choked_mass_flow(7e6, 0, 0.01)
    with pytest.raises(InvalidNozzleInputError):
        choked_mass_flow(7e6, 3500.0, 0)


def test_exit_mach_from_area_ratio_round_trips_with_area_mach_ratio() -> None:
    for mach in (1.5, 2.0, 3.0, 4.0):
        area_ratio = area_mach_ratio(mach)
        recovered = exit_mach_from_area_ratio(area_ratio)
        assert math.isclose(recovered, mach, rel_tol=1e-5)


def test_exit_mach_from_area_ratio_sonic_at_unity() -> None:
    assert math.isclose(exit_mach_from_area_ratio(1.0), 1.0, rel_tol=1e-9)


def test_exit_mach_from_area_ratio_subsonic_branch_is_subsonic() -> None:
    mach = exit_mach_from_area_ratio(1.6875, supersonic=False)
    assert mach < 1.0
    assert math.isclose(area_mach_ratio(mach), 1.6875, rel_tol=1e-3)


def test_exit_mach_from_area_ratio_rejects_ratio_below_one() -> None:
    with pytest.raises(InvalidNozzleInputError):
        exit_mach_from_area_ratio(0.5)


def test_nozzle_exit_conditions_matches_isentropic_relation() -> None:
    tc, mach, gamma = 3500.0, 2.5, 1.22
    te, ve = nozzle_exit_conditions(tc, mach, gamma=gamma)
    expected_te = tc / (1 + (gamma - 1) / 2 * mach**2)
    assert math.isclose(te, expected_te, rel_tol=1e-9)
    assert math.isclose(ve, mach * math.sqrt(gamma * 287.05287 * te), rel_tol=1e-9)


def test_nozzle_exit_temperature_below_chamber_temperature() -> None:
    te, _ = nozzle_exit_conditions(3500.0, 2.5, gamma=1.22)
    assert te < 3500.0


def test_nozzle_exit_conditions_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidNozzleInputError):
        nozzle_exit_conditions(0, 2.5)
    with pytest.raises(InvalidNozzleInputError):
        nozzle_exit_conditions(3500.0, 0)
