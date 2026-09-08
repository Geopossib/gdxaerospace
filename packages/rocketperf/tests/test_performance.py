"""Validate rocket performance relations against hand calculations."""

from __future__ import annotations

import math

import pytest
from rocketperf.exceptions import InvalidRocketInputError
from rocketperf.performance import (
    characteristic_velocity,
    effective_exhaust_velocity,
    ideal_delta_v,
    mass_ratio_for_delta_v,
    specific_impulse_rocket,
    thrust_coefficient,
)


def test_effective_exhaust_velocity_matches_formula() -> None:
    c = effective_exhaust_velocity(thrust=100_000.0, mdot_propellant=40.0)
    assert math.isclose(c, 2500.0, rel_tol=1e-9)


def test_effective_exhaust_velocity_rejects_nonpositive_inputs() -> None:
    with pytest.raises(InvalidRocketInputError):
        effective_exhaust_velocity(thrust=0, mdot_propellant=40.0)
    with pytest.raises(InvalidRocketInputError):
        effective_exhaust_velocity(thrust=100_000.0, mdot_propellant=0)


def test_specific_impulse_matches_formula() -> None:
    isp = specific_impulse_rocket(2500.0)
    assert math.isclose(isp, 2500.0 / 9.80665, rel_tol=1e-9)


def test_typical_chemical_rocket_isp_is_physically_reasonable() -> None:
    """Chemical rocket Isp typically falls in ~200-450 s (Sutton, Ch. 2)."""
    isp = specific_impulse_rocket(effective_exhaust_velocity(100_000.0, 30.0))
    assert 200 < isp < 500


def test_characteristic_velocity_matches_formula() -> None:
    c_star = characteristic_velocity(chamber_pressure=7e6, throat_area=0.01, mdot=40.0)
    assert math.isclose(c_star, 1750.0, rel_tol=1e-9)


def test_characteristic_velocity_rejects_nonpositive_inputs() -> None:
    with pytest.raises(InvalidRocketInputError):
        characteristic_velocity(chamber_pressure=0, throat_area=0.01, mdot=40.0)
    with pytest.raises(InvalidRocketInputError):
        characteristic_velocity(chamber_pressure=7e6, throat_area=0, mdot=40.0)
    with pytest.raises(InvalidRocketInputError):
        characteristic_velocity(chamber_pressure=7e6, throat_area=0.01, mdot=0)


def test_thrust_coefficient_matches_formula() -> None:
    cf = thrust_coefficient(thrust=100_000.0, chamber_pressure=7e6, throat_area=0.01)
    assert math.isclose(cf, 100_000.0 / (7e6 * 0.01), rel_tol=1e-9)


def test_thrust_coefficient_typical_range() -> None:
    """Well-designed nozzles typically give CF in ~1.4-2.0 (Sutton, Ch. 3)."""
    cf = thrust_coefficient(thrust=100_000.0, chamber_pressure=7e6, throat_area=0.01)
    assert 1.0 < cf < 2.2


def test_ideal_delta_v_matches_tsiolkovsky_formula() -> None:
    c, m0, mf = 2500.0, 1000.0, 400.0
    dv = ideal_delta_v(c, m0, mf)
    assert math.isclose(dv, c * math.log(m0 / mf), rel_tol=1e-9)


def test_ideal_delta_v_rejects_invalid_mass_ordering() -> None:
    with pytest.raises(InvalidRocketInputError):
        ideal_delta_v(2500.0, mass_initial=400.0, mass_final=1000.0)
    with pytest.raises(InvalidRocketInputError):
        ideal_delta_v(2500.0, mass_initial=400.0, mass_final=400.0)


def test_mass_ratio_round_trips_with_delta_v() -> None:
    c, m0, mf = 2500.0, 1000.0, 400.0
    dv = ideal_delta_v(c, m0, mf)
    ratio = mass_ratio_for_delta_v(dv, c)
    assert math.isclose(ratio, m0 / mf, rel_tol=1e-6)


def test_mass_ratio_and_delta_v_reject_nonpositive_inputs() -> None:
    with pytest.raises(InvalidRocketInputError):
        mass_ratio_for_delta_v(delta_v=0, effective_exhaust_velocity_=2500.0)
    with pytest.raises(InvalidRocketInputError):
        mass_ratio_for_delta_v(delta_v=1000.0, effective_exhaust_velocity_=0)
