"""Validate the floating-potential current-balance derivation."""

from __future__ import annotations

import math

import pytest
from plasmaspace.charging import electron_thermal_flux, floating_potential, ion_bohm_flux
from plasmaspace.exceptions import InvalidSpacePlasmaInputError
from plasmathrust.constants import ELECTRON_MASS, ELEMENTARY_CHARGE, ION_MASS


def test_electron_thermal_flux_matches_formula() -> None:
    n_e, te_ev = 1e12, 3.0
    kte = te_ev * ELEMENTARY_CHARGE
    v_bar = math.sqrt(8 * kte / (math.pi * ELECTRON_MASS))
    expected = n_e * v_bar / 4
    assert math.isclose(electron_thermal_flux(n_e, te_ev), expected, rel_tol=1e-9)


def test_electron_thermal_flux_rejects_nonpositive_inputs() -> None:
    with pytest.raises(InvalidSpacePlasmaInputError):
        electron_thermal_flux(0, 3.0)
    with pytest.raises(InvalidSpacePlasmaInputError):
        electron_thermal_flux(1e12, 0)


def test_ion_bohm_flux_far_smaller_than_electron_thermal_flux() -> None:
    """This asymmetry is exactly why an isolated surface charges negative."""
    n_e, te_ev, mass = 1e12, 3.0, ION_MASS["argon"]
    e_flux = electron_thermal_flux(n_e, te_ev)
    i_flux = ion_bohm_flux(n_e, te_ev, mass)
    assert i_flux < e_flux


def test_ion_bohm_flux_rejects_nonpositive_density() -> None:
    with pytest.raises(InvalidSpacePlasmaInputError):
        ion_bohm_flux(0, 3.0, ION_MASS["argon"])


def test_floating_potential_matches_derivation() -> None:
    te_ev, mass = 3.0, ION_MASS["argon"]
    expected = -(te_ev / 2) * math.log(mass / (2 * math.pi * ELECTRON_MASS))
    assert math.isclose(floating_potential(te_ev, mass), expected, rel_tol=1e-9)


def test_floating_potential_is_always_negative() -> None:
    """An isolated conductor in a plasma always floats negative of the plasma
    potential (in this idealized model with no photoemission/secondary emission)."""
    for propellant in ("argon", "xenon", "krypton", "hydrogen"):
        assert floating_potential(3.0, ION_MASS[propellant]) < 0


def test_floating_potential_scales_linearly_with_temperature() -> None:
    mass = ION_MASS["argon"]
    v_low = floating_potential(1.0, mass)
    v_high = floating_potential(3.0, mass)
    assert math.isclose(v_high / v_low, 3.0, rel_tol=1e-9)


def test_floating_potential_heavier_ion_gives_more_negative_potential() -> None:
    """A heavier ion is slower (lower Bohm flux), requiring a stronger
    retarding field -- and hence a more negative floating potential --
    to balance the electron flux."""
    v_argon = floating_potential(3.0, ION_MASS["argon"])
    v_xenon = floating_potential(3.0, ION_MASS["xenon"])
    assert v_xenon < v_argon


def test_floating_potential_argon_matches_known_reference_coefficient() -> None:
    """Argon's floating-potential coefficient is a well-known reference value
    (~4.68 * Te[eV]) from Lieberman & Lichtenberg."""
    te_ev = 5.0
    v_f = floating_potential(te_ev, ION_MASS["argon"])
    assert math.isclose(v_f / te_ev, -4.68, rel_tol=1e-2)


def test_floating_potential_rejects_nonpositive_inputs() -> None:
    with pytest.raises(InvalidSpacePlasmaInputError):
        floating_potential(0, ION_MASS["argon"])
    with pytest.raises(InvalidSpacePlasmaInputError):
        floating_potential(3.0, 0)
