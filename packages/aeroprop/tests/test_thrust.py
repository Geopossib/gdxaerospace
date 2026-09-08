"""Validate general propulsion performance relations."""

from __future__ import annotations

import math

import pytest
from aeroprop.exceptions import InvalidPropulsionInputError
from aeroprop.thrust import (
    propulsive_efficiency,
    specific_impulse,
    thrust_airbreathing,
    thrust_specific_fuel_consumption,
)


def test_thrust_airbreathing_matches_hand_calculation() -> None:
    thrust = thrust_airbreathing(
        mdot_air=50.0, mdot_fuel=1.0, exit_velocity=600.0, flight_velocity=250.0
    )
    expected = (50.0 + 1.0) * 600.0 - 50.0 * 250.0
    assert math.isclose(thrust, expected, rel_tol=1e-9)


def test_thrust_airbreathing_includes_pressure_term_when_supplied() -> None:
    base = thrust_airbreathing(50.0, 1.0, 600.0, 250.0)
    with_pressure = thrust_airbreathing(
        50.0, 1.0, 600.0, 250.0, exit_pressure=105_000, ambient_pressure=101_325, exit_area=0.5
    )
    assert with_pressure > base
    assert math.isclose(with_pressure - base, (105_000 - 101_325) * 0.5, rel_tol=1e-9)


def test_thrust_airbreathing_rejects_invalid_flows() -> None:
    with pytest.raises(InvalidPropulsionInputError):
        thrust_airbreathing(mdot_air=0, mdot_fuel=1.0, exit_velocity=600.0, flight_velocity=250.0)
    with pytest.raises(InvalidPropulsionInputError):
        thrust_airbreathing(
            mdot_air=50.0, mdot_fuel=-1.0, exit_velocity=600.0, flight_velocity=250.0
        )


def test_specific_impulse_matches_formula() -> None:
    isp = specific_impulse(thrust=1000.0, mdot_propellant=0.34)
    assert math.isclose(isp, 1000.0 / (0.34 * 9.80665), rel_tol=1e-9)


def test_specific_impulse_rejects_nonpositive_inputs() -> None:
    with pytest.raises(InvalidPropulsionInputError):
        specific_impulse(thrust=0, mdot_propellant=0.34)
    with pytest.raises(InvalidPropulsionInputError):
        specific_impulse(thrust=1000.0, mdot_propellant=0)


def test_tsfc_matches_formula() -> None:
    tsfc = thrust_specific_fuel_consumption(mdot_fuel=1.0, thrust=18100.0)
    assert math.isclose(tsfc, 1.0 / 18100.0, rel_tol=1e-9)


def test_tsfc_rejects_nonpositive_inputs() -> None:
    with pytest.raises(InvalidPropulsionInputError):
        thrust_specific_fuel_consumption(mdot_fuel=0, thrust=1000.0)
    with pytest.raises(InvalidPropulsionInputError):
        thrust_specific_fuel_consumption(mdot_fuel=1.0, thrust=0)


def test_propulsive_efficiency_matches_froude_formula() -> None:
    eta = propulsive_efficiency(flight_velocity=250.0, exit_velocity=600.0)
    assert math.isclose(eta, 2 * 250.0 / (250.0 + 600.0), rel_tol=1e-9)


def test_propulsive_efficiency_approaches_one_as_exit_velocity_nears_flight_velocity() -> None:
    """As Ve -> V0 (minimal jet excess velocity), efficiency -> 1 (ideal, but zero thrust)."""
    eta_close = propulsive_efficiency(flight_velocity=250.0, exit_velocity=260.0)
    eta_far = propulsive_efficiency(flight_velocity=250.0, exit_velocity=800.0)
    assert eta_close > eta_far


def test_propulsive_efficiency_rejects_exit_velocity_not_exceeding_flight_velocity() -> None:
    with pytest.raises(InvalidPropulsionInputError):
        propulsive_efficiency(flight_velocity=250.0, exit_velocity=250.0)
    with pytest.raises(InvalidPropulsionInputError):
        propulsive_efficiency(flight_velocity=250.0, exit_velocity=200.0)
