"""Validate lumped-capacitance transient response and spacecraft equilibrium temperature."""

from __future__ import annotations

import math

import pytest
from aerothermal.exceptions import InvalidThermalInputError
from aerothermal.transient import (
    lumped_capacitance_temperature,
    spacecraft_equilibrium_temperature,
)


def test_lumped_capacitance_zero_time_returns_initial_temperature() -> None:
    t = lumped_capacitance_temperature(400.0, 300.0, 25.0, 0.1, 2700.0, 0.001, 900.0, 0.0)
    assert math.isclose(t, 400.0, rel_tol=1e-9)


def test_lumped_capacitance_approaches_ambient_as_time_increases() -> None:
    t_early = lumped_capacitance_temperature(400.0, 300.0, 25.0, 0.1, 2700.0, 0.001, 900.0, 10.0)
    t_late = lumped_capacitance_temperature(
        400.0, 300.0, 25.0, 0.1, 2700.0, 0.001, 900.0, 10000.0
    )
    assert 300.0 < t_late < t_early < 400.0
    assert math.isclose(t_late, 300.0, abs_tol=0.1)


def test_lumped_capacitance_matches_exponential_formula() -> None:
    ti, ta, h, a, rho, v, c, t = 400.0, 300.0, 25.0, 0.1, 2700.0, 0.001, 900.0, 60.0
    tau = (rho * v * c) / (h * a)
    expected = ta + (ti - ta) * math.exp(-t / tau)
    assert math.isclose(
        lumped_capacitance_temperature(ti, ta, h, a, rho, v, c, t), expected, rel_tol=1e-9
    )


def test_lumped_capacitance_heating_case() -> None:
    """If initial temperature is below ambient, the body should heat up over time."""
    t = lumped_capacitance_temperature(250.0, 300.0, 25.0, 0.1, 2700.0, 0.001, 900.0, 60.0)
    assert 250.0 < t < 300.0


def test_lumped_capacitance_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidThermalInputError):
        lumped_capacitance_temperature(400.0, 300.0, 0, 0.1, 2700.0, 0.001, 900.0, 60.0)
    with pytest.raises(InvalidThermalInputError):
        lumped_capacitance_temperature(400.0, 300.0, 25.0, 0.1, 2700.0, 0.001, 900.0, -1.0)


def test_spacecraft_equilibrium_temperature_matches_formula() -> None:
    from aerothermal.heat_transfer import STEFAN_BOLTZMANN_CONSTANT

    s, alpha, eps, a_abs, a_emit = 1361.0, 0.2, 0.85, 1.0, 4.0
    expected = (alpha * s * a_abs / (eps * STEFAN_BOLTZMANN_CONSTANT * a_emit)) ** 0.25
    assert math.isclose(
        spacecraft_equilibrium_temperature(s, alpha, eps, a_abs, a_emit), expected, rel_tol=1e-9
    )


def test_spacecraft_equilibrium_temperature_higher_absorptivity_gives_higher_temp() -> None:
    low_alpha = spacecraft_equilibrium_temperature(1361.0, 0.1, 0.85, 1.0, 4.0)
    high_alpha = spacecraft_equilibrium_temperature(1361.0, 0.5, 0.85, 1.0, 4.0)
    assert high_alpha > low_alpha


def test_spacecraft_equilibrium_temperature_higher_emissivity_gives_lower_temp() -> None:
    """A better radiator (higher emissivity) sheds heat more effectively -> cooler equilibrium."""
    low_eps = spacecraft_equilibrium_temperature(1361.0, 0.2, 0.3, 1.0, 4.0)
    high_eps = spacecraft_equilibrium_temperature(1361.0, 0.2, 0.9, 1.0, 4.0)
    assert high_eps < low_eps


def test_spacecraft_equilibrium_temperature_reasonable_for_leo_satellite() -> None:
    """A typical satellite equilibrium temperature should be in a physically
    plausible range (not near absolute zero, not absurdly hot)."""
    t = spacecraft_equilibrium_temperature(1361.0, 0.2, 0.85, 1.0, 4.0)
    assert 100 < t < 400


def test_spacecraft_equilibrium_temperature_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidThermalInputError):
        spacecraft_equilibrium_temperature(0, 0.2, 0.85, 1.0, 4.0)
    with pytest.raises(InvalidThermalInputError):
        spacecraft_equilibrium_temperature(1361.0, 1.5, 0.85, 1.0, 4.0)
    with pytest.raises(InvalidThermalInputError):
        spacecraft_equilibrium_temperature(1361.0, 0.2, 0, 1.0, 4.0)
    with pytest.raises(InvalidThermalInputError):
        spacecraft_equilibrium_temperature(1361.0, 0.2, 0.85, 0, 4.0)
    with pytest.raises(InvalidThermalInputError):
        spacecraft_equilibrium_temperature(1361.0, 0.2, 0.85, 1.0, 0)
