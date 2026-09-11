"""Validate conduction, convection, radiation, and thermal resistance formulas."""

from __future__ import annotations

import math

import pytest
from aerothermal.exceptions import InvalidThermalInputError
from aerothermal.heat_transfer import (
    STEFAN_BOLTZMANN_CONSTANT,
    conduction_heat_transfer,
    convection_heat_transfer,
    parallel_resistance,
    radiation_heat_transfer,
    series_resistance,
    thermal_resistance_conduction,
    thermal_resistance_convection,
)


def test_conduction_matches_fouriers_law() -> None:
    k, a, dt, length = 200.0, 0.5, 50.0, 0.01
    assert math.isclose(
        conduction_heat_transfer(k, a, dt, length), k * a * dt / length, rel_tol=1e-9
    )


def test_conduction_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidThermalInputError):
        conduction_heat_transfer(0, 0.5, 50.0, 0.01)
    with pytest.raises(InvalidThermalInputError):
        conduction_heat_transfer(200.0, 0, 50.0, 0.01)
    with pytest.raises(InvalidThermalInputError):
        conduction_heat_transfer(200.0, 0.5, 50.0, 0)


def test_convection_matches_newtons_law() -> None:
    h, a, dt = 25.0, 2.0, 30.0
    assert math.isclose(convection_heat_transfer(h, a, dt), h * a * dt, rel_tol=1e-9)


def test_convection_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidThermalInputError):
        convection_heat_transfer(0, 2.0, 30.0)
    with pytest.raises(InvalidThermalInputError):
        convection_heat_transfer(25.0, 0, 30.0)


def test_radiation_matches_stefan_boltzmann_law() -> None:
    eps, a, th, tc = 0.9, 1.0, 400.0, 300.0
    expected = eps * STEFAN_BOLTZMANN_CONSTANT * a * (th**4 - tc**4)
    assert math.isclose(radiation_heat_transfer(eps, a, th, tc), expected, rel_tol=1e-9)


def test_radiation_zero_at_equal_temperatures() -> None:
    assert radiation_heat_transfer(0.9, 1.0, 300.0, 300.0) == 0.0


def test_radiation_negative_when_cold_exceeds_hot() -> None:
    """If 'cold' is actually hotter, net radiative transfer should be negative
    (heat flows the other way)."""
    assert radiation_heat_transfer(0.9, 1.0, 300.0, 400.0) < 0


def test_radiation_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidThermalInputError):
        radiation_heat_transfer(0, 1.0, 400.0, 300.0)
    with pytest.raises(InvalidThermalInputError):
        radiation_heat_transfer(1.5, 1.0, 400.0, 300.0)
    with pytest.raises(InvalidThermalInputError):
        radiation_heat_transfer(0.9, 1.0, 0, 300.0)


def test_thermal_resistance_conduction_matches_formula() -> None:
    length, k, a = 0.01, 200.0, 0.5
    assert math.isclose(
        thermal_resistance_conduction(length, k, a), length / (k * a), rel_tol=1e-9
    )


def test_thermal_resistance_convection_matches_formula() -> None:
    h, a = 25.0, 2.0
    assert math.isclose(thermal_resistance_convection(h, a), 1 / (h * a), rel_tol=1e-9)


def test_series_resistance_sums_directly() -> None:
    assert math.isclose(series_resistance(0.01, 0.02, 0.03), 0.06, rel_tol=1e-9)


def test_series_resistance_rejects_empty_and_nonpositive() -> None:
    with pytest.raises(InvalidThermalInputError):
        series_resistance()
    with pytest.raises(InvalidThermalInputError):
        series_resistance(0.01, -0.02)


def test_parallel_resistance_matches_formula() -> None:
    r1, r2 = 0.02, 0.03
    expected = 1 / (1 / r1 + 1 / r2)
    assert math.isclose(parallel_resistance(r1, r2), expected, rel_tol=1e-9)


def test_parallel_resistance_equal_resistors_halves() -> None:
    assert math.isclose(parallel_resistance(0.02, 0.02), 0.01, rel_tol=1e-9)


def test_parallel_resistance_always_less_than_smallest_series_resistor() -> None:
    r_parallel = parallel_resistance(0.01, 0.02, 0.03)
    assert r_parallel < 0.01


def test_parallel_resistance_rejects_empty_and_nonpositive() -> None:
    with pytest.raises(InvalidThermalInputError):
        parallel_resistance()
    with pytest.raises(InvalidThermalInputError):
        parallel_resistance(0.02, 0)
