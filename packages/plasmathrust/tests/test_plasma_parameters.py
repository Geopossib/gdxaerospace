"""Validate fundamental plasma-parameter relations."""

from __future__ import annotations

import math

import pytest
from plasmathrust.constants import ELECTRON_MASS, ELEMENTARY_CHARGE, ION_MASS, VACUUM_PERMITTIVITY
from plasmathrust.exceptions import InvalidPlasmaParameterError
from plasmathrust.plasma_parameters import (
    bohm_velocity,
    debye_length,
    electron_cyclotron_frequency,
    hall_parameter,
    ion_cyclotron_frequency,
    larmor_radius,
    plasma_frequency,
)


def test_debye_length_matches_formula() -> None:
    n_e, te_ev = 1e18, 20.0
    kte = te_ev * ELEMENTARY_CHARGE
    expected = math.sqrt(VACUUM_PERMITTIVITY * kte / (n_e * ELEMENTARY_CHARGE**2))
    assert math.isclose(debye_length(n_e, te_ev), expected, rel_tol=1e-9)


def test_debye_length_typical_hall_thruster_order_of_magnitude() -> None:
    """Hall-thruster plasma Debye lengths are typically tens of microns."""
    length = debye_length(electron_density=1e18, electron_temperature_ev=20.0)
    assert 1e-6 < length < 1e-3


def test_debye_length_decreases_with_density() -> None:
    low_density = debye_length(1e16, 20.0)
    high_density = debye_length(1e18, 20.0)
    assert high_density < low_density


def test_debye_length_rejects_nonpositive_inputs() -> None:
    with pytest.raises(InvalidPlasmaParameterError):
        debye_length(0, 20.0)
    with pytest.raises(InvalidPlasmaParameterError):
        debye_length(1e18, 0)


def test_plasma_frequency_matches_formula() -> None:
    n_e = 1e18
    expected = math.sqrt(n_e * ELEMENTARY_CHARGE**2 / (VACUUM_PERMITTIVITY * ELECTRON_MASS))
    assert math.isclose(plasma_frequency(n_e), expected, rel_tol=1e-9)


def test_plasma_frequency_rejects_nonpositive_density() -> None:
    with pytest.raises(InvalidPlasmaParameterError):
        plasma_frequency(0)


def test_electron_cyclotron_frequency_matches_formula() -> None:
    b = 0.02
    expected = ELEMENTARY_CHARGE * b / ELECTRON_MASS
    assert math.isclose(electron_cyclotron_frequency(b), expected, rel_tol=1e-9)


def test_electron_cyclotron_frequency_rejects_nonpositive_field() -> None:
    with pytest.raises(InvalidPlasmaParameterError):
        electron_cyclotron_frequency(0)


def test_ion_cyclotron_frequency_much_smaller_than_electron() -> None:
    """Ions are far heavier than electrons, so gyrate far more slowly at the same B."""
    b = 0.02
    omega_ce = electron_cyclotron_frequency(b)
    omega_ci = ion_cyclotron_frequency(b, ION_MASS["xenon"])
    assert omega_ci < omega_ce / 1000


def test_ion_cyclotron_frequency_scales_with_charge_number() -> None:
    b, mass = 0.02, ION_MASS["xenon"]
    singly = ion_cyclotron_frequency(b, mass, charge_number=1)
    doubly = ion_cyclotron_frequency(b, mass, charge_number=2)
    assert math.isclose(doubly, 2 * singly, rel_tol=1e-9)


def test_ion_cyclotron_frequency_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidPlasmaParameterError):
        ion_cyclotron_frequency(0, ION_MASS["xenon"])
    with pytest.raises(InvalidPlasmaParameterError):
        ion_cyclotron_frequency(0.02, 0)
    with pytest.raises(InvalidPlasmaParameterError):
        ion_cyclotron_frequency(0.02, ION_MASS["xenon"], charge_number=0)


def test_larmor_radius_matches_formula() -> None:
    mass, v_perp, b = ELECTRON_MASS, 1e6, 0.02
    expected = mass * v_perp / (ELEMENTARY_CHARGE * b)
    assert math.isclose(larmor_radius(mass, v_perp, b), expected, rel_tol=1e-9)


def test_larmor_radius_zero_at_zero_perpendicular_velocity() -> None:
    assert larmor_radius(ELECTRON_MASS, 0.0, 0.02) == 0.0


def test_larmor_radius_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidPlasmaParameterError):
        larmor_radius(0, 1e6, 0.02)
    with pytest.raises(InvalidPlasmaParameterError):
        larmor_radius(ELECTRON_MASS, -1.0, 0.02)
    with pytest.raises(InvalidPlasmaParameterError):
        larmor_radius(ELECTRON_MASS, 1e6, 0)


def test_hall_parameter_matches_formula() -> None:
    assert math.isclose(hall_parameter(1e8, 1e6), 100.0, rel_tol=1e-9)


def test_hall_parameter_rejects_nonpositive_inputs() -> None:
    with pytest.raises(InvalidPlasmaParameterError):
        hall_parameter(0, 1e6)
    with pytest.raises(InvalidPlasmaParameterError):
        hall_parameter(1e8, 0)


def test_bohm_velocity_matches_formula() -> None:
    te_ev, mass = 3.0, ION_MASS["argon"]
    expected = math.sqrt(te_ev * ELEMENTARY_CHARGE / mass)
    assert math.isclose(bohm_velocity(te_ev, mass), expected, rel_tol=1e-9)


def test_bohm_velocity_lighter_ion_is_faster() -> None:
    """At the same Te, a lighter ion has a higher Bohm (sound) velocity."""
    v_argon = bohm_velocity(3.0, ION_MASS["argon"])
    v_xenon = bohm_velocity(3.0, ION_MASS["xenon"])
    assert v_argon > v_xenon


def test_bohm_velocity_rejects_nonpositive_inputs() -> None:
    with pytest.raises(InvalidPlasmaParameterError):
        bohm_velocity(0, ION_MASS["argon"])
    with pytest.raises(InvalidPlasmaParameterError):
        bohm_velocity(3.0, 0)
