"""Numerical validation tests for dynamic pressure, Mach, Reynolds, viscosity."""

from __future__ import annotations

import math

import pytest
from aerocalc.exceptions import InvalidMachNumberError
from aerocalc.flow import (
    dynamic_pressure,
    mach_number,
    reynolds_number,
    sutherland_viscosity,
)


def test_dynamic_pressure_textbook_value() -> None:
    """q = 1/2 * rho * V^2; sea-level air at 100 m/s -> 6125 Pa."""
    q = dynamic_pressure(density=1.225, velocity=100)
    assert math.isclose(q, 6125.0, rel_tol=1e-9)


def test_dynamic_pressure_rejects_nonpositive_density() -> None:
    with pytest.raises(ValueError):
        dynamic_pressure(density=0, velocity=100)
    with pytest.raises(ValueError):
        dynamic_pressure(density=-1.2, velocity=100)


def test_mach_number_sonic() -> None:
    assert math.isclose(mach_number(velocity=343.0, speed_of_sound=343.0), 1.0)


def test_mach_number_uses_velocity_magnitude() -> None:
    assert mach_number(velocity=-200.0, speed_of_sound=340.0) == mach_number(
        velocity=200.0, speed_of_sound=340.0
    )


def test_mach_number_rejects_nonpositive_speed_of_sound() -> None:
    with pytest.raises(InvalidMachNumberError):
        mach_number(velocity=100.0, speed_of_sound=0.0)


def test_sutherland_viscosity_sea_level_reference() -> None:
    """mu(288.15 K) ~= 1.789e-5 Pa*s, the standard sea-level reference value."""
    mu = sutherland_viscosity(288.15)
    assert math.isclose(mu, 1.789e-5, rel_tol=2e-3)


def test_sutherland_viscosity_increases_with_temperature() -> None:
    """Gas viscosity increases with temperature (unlike liquids)."""
    assert sutherland_viscosity(400.0) > sutherland_viscosity(250.0)


def test_sutherland_viscosity_rejects_nonpositive_temperature() -> None:
    with pytest.raises(ValueError):
        sutherland_viscosity(0.0)
    with pytest.raises(ValueError):
        sutherland_viscosity(-10.0)


def test_reynolds_number_matches_hand_calculation() -> None:
    """Re = rho*V*L/mu computed directly should match the helper to high precision."""
    density, velocity, length, temperature = 1.225, 50.0, 1.0, 288.15
    mu = sutherland_viscosity(temperature)
    expected = density * velocity * length / mu
    actual = reynolds_number(
        density=density, velocity=velocity, length=length, temperature=temperature
    )
    assert math.isclose(actual, expected, rel_tol=1e-9)
    # Sanity check against the known order of magnitude for this case (~3.4e6).
    assert 3.3e6 < actual < 3.5e6


def test_reynolds_number_explicit_viscosity_overrides_temperature() -> None:
    """If dynamic_viscosity is given explicitly, temperature is ignored."""
    re_explicit = reynolds_number(
        density=1.0, velocity=10.0, length=1.0, dynamic_viscosity=1.8e-5
    )
    re_from_temp_but_overridden = reynolds_number(
        density=1.0,
        velocity=10.0,
        length=1.0,
        temperature=500.0,  # should be ignored since dynamic_viscosity is set
        dynamic_viscosity=1.8e-5,
    )
    assert re_explicit == re_from_temp_but_overridden


def test_reynolds_number_requires_viscosity_or_temperature() -> None:
    with pytest.raises(ValueError):
        reynolds_number(density=1.2, velocity=10.0, length=1.0)


@pytest.mark.parametrize("bad_density", [0, -1.0])
def test_reynolds_number_rejects_nonpositive_density(bad_density: float) -> None:
    with pytest.raises(ValueError):
        reynolds_number(density=bad_density, velocity=10.0, length=1.0, temperature=288.15)


@pytest.mark.parametrize("bad_length", [0, -1.0])
def test_reynolds_number_rejects_nonpositive_length(bad_length: float) -> None:
    with pytest.raises(ValueError):
        reynolds_number(density=1.2, velocity=10.0, length=bad_length, temperature=288.15)
