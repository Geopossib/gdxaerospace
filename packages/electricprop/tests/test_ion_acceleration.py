"""Validate ideal electrostatic ion-thruster performance relations."""

from __future__ import annotations

import math

import pytest
from electricprop.exceptions import InvalidElectricPropulsionInputError
from electricprop.ion_acceleration import (
    ion_exhaust_velocity,
    specific_impulse_electric,
    thrust_efficiency,
    thrust_from_beam_current,
)
from electricprop.thrusters import HallThruster, IonThruster
from plasmathrust.constants import ELEMENTARY_CHARGE, ION_MASS


def test_ion_exhaust_velocity_matches_formula() -> None:
    v, mass = 300.0, ION_MASS["xenon"]
    expected = math.sqrt(2 * ELEMENTARY_CHARGE * v / mass)
    assert math.isclose(ion_exhaust_velocity(v, mass), expected, rel_tol=1e-9)


def test_ion_exhaust_velocity_scales_with_sqrt_voltage() -> None:
    mass = ION_MASS["xenon"]
    v_low = ion_exhaust_velocity(100.0, mass)
    v_high = ion_exhaust_velocity(400.0, mass)
    assert math.isclose(v_high / v_low, 2.0, rel_tol=1e-9)  # sqrt(400/100) = 2


def test_ion_exhaust_velocity_lighter_ion_is_faster() -> None:
    """At the same voltage, a lighter ion reaches higher exhaust velocity."""
    v_xenon = ion_exhaust_velocity(300.0, ION_MASS["xenon"])
    v_argon = ion_exhaust_velocity(300.0, ION_MASS["argon"])
    assert v_argon > v_xenon


def test_ion_exhaust_velocity_scales_with_sqrt_charge_number() -> None:
    mass = ION_MASS["xenon"]
    v_single = ion_exhaust_velocity(300.0, mass, charge_number=1)
    v_double = ion_exhaust_velocity(300.0, mass, charge_number=2)
    assert math.isclose(v_double / v_single, math.sqrt(2), rel_tol=1e-9)


def test_ion_exhaust_velocity_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidElectricPropulsionInputError):
        ion_exhaust_velocity(0, ION_MASS["xenon"])
    with pytest.raises(InvalidElectricPropulsionInputError):
        ion_exhaust_velocity(300.0, 0)
    with pytest.raises(InvalidElectricPropulsionInputError):
        ion_exhaust_velocity(300.0, ION_MASS["xenon"], charge_number=0)


def test_thrust_from_beam_current_matches_formula() -> None:
    ib, v, mass = 5.0, 300.0, ION_MASS["xenon"]
    expected = ib * math.sqrt(2 * mass * v / ELEMENTARY_CHARGE)
    assert math.isclose(thrust_from_beam_current(ib, v, mass), expected, rel_tol=1e-9)


def test_thrust_from_beam_current_scales_linearly_with_current() -> None:
    v, mass = 300.0, ION_MASS["xenon"]
    f1 = thrust_from_beam_current(1.0, v, mass)
    f5 = thrust_from_beam_current(5.0, v, mass)
    assert math.isclose(f5, 5 * f1, rel_tol=1e-9)


def test_thrust_from_beam_current_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidElectricPropulsionInputError):
        thrust_from_beam_current(0, 300.0, ION_MASS["xenon"])
    with pytest.raises(InvalidElectricPropulsionInputError):
        thrust_from_beam_current(5.0, 0, ION_MASS["xenon"])
    with pytest.raises(InvalidElectricPropulsionInputError):
        thrust_from_beam_current(5.0, 300.0, 0)


def test_specific_impulse_electric_matches_formula() -> None:
    ve = 20998.4
    assert math.isclose(specific_impulse_electric(ve), ve / 9.80665, rel_tol=1e-9)


def test_specific_impulse_electric_rejects_nonpositive_velocity() -> None:
    with pytest.raises(InvalidElectricPropulsionInputError):
        specific_impulse_electric(0)


def test_thrust_efficiency_matches_formula() -> None:
    f, mdot, p = 0.105, 5e-6, 1500.0
    expected = f**2 / (2 * mdot * p)
    assert math.isclose(thrust_efficiency(f, mdot, p), expected, rel_tol=1e-9)


def test_thrust_efficiency_in_physically_plausible_range() -> None:
    """Total efficiency for a well-designed electric thruster is well under 1."""
    eta = thrust_efficiency(thrust=0.105, mdot=5e-6, power=1500.0)
    assert 0 < eta < 1


def test_thrust_efficiency_rejects_nonpositive_inputs() -> None:
    with pytest.raises(InvalidElectricPropulsionInputError):
        thrust_efficiency(0, 5e-6, 1500.0)
    with pytest.raises(InvalidElectricPropulsionInputError):
        thrust_efficiency(0.105, 0, 1500.0)
    with pytest.raises(InvalidElectricPropulsionInputError):
        thrust_efficiency(0.105, 5e-6, 0)


def test_hall_thruster_class_methods_are_internally_consistent() -> None:
    """HallThruster's methods must reduce to the underlying free functions."""
    thruster = HallThruster(voltage=300.0, current=5.0, mass_flow=5e-6)
    ve = ion_exhaust_velocity(300.0, ION_MASS["xenon"])
    assert math.isclose(thruster.exhaust_velocity(), ve, rel_tol=1e-9)
    assert math.isclose(thruster.thrust(), 5e-6 * ve, rel_tol=1e-9)
    assert math.isclose(thruster.power(), 1500.0, rel_tol=1e-9)
    assert math.isclose(
        thruster.specific_impulse(), specific_impulse_electric(ve), rel_tol=1e-9
    )
    assert math.isclose(
        thruster.efficiency(),
        thrust_efficiency(thruster.thrust(), 5e-6, 1500.0),
        rel_tol=1e-9,
    )


def test_ion_thruster_higher_voltage_gives_higher_isp_than_hall_thruster() -> None:
    """Gridded ion thrusters typically run at higher voltage -> higher Isp than Hall thrusters."""
    hall = HallThruster(voltage=300.0, current=5.0, mass_flow=5e-6)
    ion = IonThruster(voltage=1200.0, current=1.76, mass_flow=3.4e-6)
    assert ion.specific_impulse() > hall.specific_impulse()


def test_thruster_class_rejects_unknown_propellant() -> None:
    thruster = HallThruster(voltage=300.0, current=5.0, mass_flow=5e-6, propellant="unobtainium")
    with pytest.raises(ValueError, match="Unknown propellant"):
        thruster.exhaust_velocity()
