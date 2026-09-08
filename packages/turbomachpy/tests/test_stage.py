"""Validate compressor/turbine stage relations."""

from __future__ import annotations

import math

import pytest
from turbomachpy.exceptions import InvalidTurbomachineryInputError
from turbomachpy.stage import compressor_temperature_rise, specific_work, turbine_temperature_drop


def test_compressor_temperature_rise_matches_formula() -> None:
    t1, pr, eta, gamma = 288.0, 8.0, 0.85, 1.4
    ideal = t1 * (pr ** ((gamma - 1) / gamma) - 1)
    expected = ideal / eta
    actual = compressor_temperature_rise(t1, pr, eta, gamma=gamma)
    assert math.isclose(actual, expected, rel_tol=1e-9)


def test_compressor_actual_rise_exceeds_ideal_rise() -> None:
    """A real (eta < 1) compressor always requires more temperature rise than ideal."""
    t1, pr, gamma = 288.0, 8.0, 1.4
    ideal = t1 * (pr ** ((gamma - 1) / gamma) - 1)
    actual = compressor_temperature_rise(t1, pr, isentropic_efficiency=0.85, gamma=gamma)
    assert actual > ideal


def test_compressor_temperature_rise_increases_with_pressure_ratio() -> None:
    low = compressor_temperature_rise(288.0, 4.0, 0.85)
    high = compressor_temperature_rise(288.0, 12.0, 0.85)
    assert high > low


def test_compressor_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidTurbomachineryInputError):
        compressor_temperature_rise(0, 8.0, 0.85)
    with pytest.raises(InvalidTurbomachineryInputError):
        compressor_temperature_rise(288.0, 1.0, 0.85)
    with pytest.raises(InvalidTurbomachineryInputError):
        compressor_temperature_rise(288.0, 8.0, 0)
    with pytest.raises(InvalidTurbomachineryInputError):
        compressor_temperature_rise(288.0, 8.0, 1.5)


def test_turbine_temperature_drop_matches_formula() -> None:
    t3, pr, eta, gamma = 1100.0, 8.0, 0.90, 1.333
    ideal = t3 * (1 - (1 / pr) ** ((gamma - 1) / gamma))
    expected = eta * ideal
    actual = turbine_temperature_drop(t3, pr, eta, gamma=gamma)
    assert math.isclose(actual, expected, rel_tol=1e-9)


def test_turbine_actual_drop_less_than_ideal_drop() -> None:
    """A real (eta < 1) turbine always extracts less temperature drop than ideal."""
    t3, pr, gamma = 1100.0, 8.0, 1.333
    ideal = t3 * (1 - (1 / pr) ** ((gamma - 1) / gamma))
    actual = turbine_temperature_drop(t3, pr, isentropic_efficiency=0.90, gamma=gamma)
    assert actual < ideal


def test_turbine_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidTurbomachineryInputError):
        turbine_temperature_drop(0, 8.0, 0.90)
    with pytest.raises(InvalidTurbomachineryInputError):
        turbine_temperature_drop(1100.0, 1.0, 0.90)
    with pytest.raises(InvalidTurbomachineryInputError):
        turbine_temperature_drop(1100.0, 8.0, 0)


def test_specific_work_matches_formula() -> None:
    assert math.isclose(specific_work(1005.0, 274.9), 1005.0 * 274.9, rel_tol=1e-9)


def test_specific_work_rejects_nonpositive_specific_heat() -> None:
    with pytest.raises(InvalidTurbomachineryInputError):
        specific_work(0, 100.0)
    with pytest.raises(InvalidTurbomachineryInputError):
        specific_work(-100.0, 100.0)


def test_compressor_and_turbine_realistic_stage_values() -> None:
    """A realistic single-spool turbojet stage: compressor work should be a
    substantial fraction of turbine work (they must balance to drive the
    compressor on a shared shaft in a real engine)."""
    compressor_dt = compressor_temperature_rise(288.0, 8.0, 0.85)
    turbine_dt = turbine_temperature_drop(1100.0, 8.0, 0.90)
    compressor_work = specific_work(1005.0, compressor_dt)
    turbine_work = specific_work(1148.0, turbine_dt)  # hot-gas cp, typically higher than cold air
    assert 0.1 < compressor_work / turbine_work < 1.0
