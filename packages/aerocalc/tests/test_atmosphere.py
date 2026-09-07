"""Validate Atmosphere against the published 1976 U.S. Standard Atmosphere table."""

from __future__ import annotations

import math

import pytest
from aerocalc.atmosphere import Atmosphere
from aerocalc.exceptions import InvalidAltitudeError

# (altitude_m, temperature_K, pressure_Pa, density_kg_m3) — published table values,
# U.S. Standard Atmosphere 1976 / ICAO Doc 7488.
_REFERENCE_TABLE = [
    (0, 288.15, 101_325.0, 1.2250),
    (11_000, 216.65, 22_632.06, 0.36392),
    (20_000, 216.65, 5_474.89, 0.088035),
    (32_000, 228.65, 868.019, 0.013225),
    (47_000, 270.65, 110.906, 0.0014275),
    (51_000, 270.65, 66.939, 0.00086161),
    (71_000, 214.65, 3.956, 0.000064210),
]


@pytest.mark.parametrize("altitude,temperature,pressure,density", _REFERENCE_TABLE)
def test_layer_base_conditions_match_standard_table(
    altitude: float, temperature: float, pressure: float, density: float
) -> None:
    atm = Atmosphere(altitude=altitude)
    assert math.isclose(atm.temperature, temperature, rel_tol=1e-4)
    assert math.isclose(atm.pressure, pressure, rel_tol=1e-3)
    assert math.isclose(atm.density, density, rel_tol=1e-3)


def test_sea_level_speed_of_sound() -> None:
    """Speed of sound at sea level ISA conditions is ~340.3 m/s."""
    atm = Atmosphere(altitude=0)
    assert math.isclose(atm.speed_of_sound, 340.29, rel_tol=1e-3)


def test_isothermal_layer_pressure_decays_exponentially() -> None:
    """Between 11 km and 20 km the ISA is isothermal; pressure follows exp decay."""
    atm_11 = Atmosphere(altitude=11_000)
    atm_15 = Atmosphere(altitude=15_000)
    assert atm_11.temperature == atm_15.temperature == pytest.approx(216.65)
    assert atm_15.pressure < atm_11.pressure


def test_temperature_decreases_monotonically_in_troposphere() -> None:
    low = Atmosphere(altitude=0)
    high = Atmosphere(altitude=10_000)
    assert high.temperature < low.temperature


@pytest.mark.parametrize("bad_altitude", [-100, 90_000, 1_000_000])
def test_out_of_range_altitude_raises(bad_altitude: float) -> None:
    with pytest.raises(InvalidAltitudeError):
        Atmosphere(altitude=bad_altitude)


def test_boundary_altitudes_are_valid() -> None:
    """0 m and 86000 m are inclusive boundaries and must not raise."""
    Atmosphere(altitude=0)
    Atmosphere(altitude=86_000)


def test_error_message_is_actionable() -> None:
    with pytest.raises(InvalidAltitudeError) as exc_info:
        Atmosphere(altitude=100_000)
    message = str(exc_info.value)
    assert "100000" in message.replace(",", "") or "100,000" in message
    assert "86000" in message.replace(",", "") or "86,000" in message
