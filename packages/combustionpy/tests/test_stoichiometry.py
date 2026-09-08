"""Validate combustion stoichiometry and the simplified temperature-rise estimate."""

from __future__ import annotations

import math

import pytest
from combustionpy.exceptions import InvalidFuelCompositionError
from combustionpy.stoichiometry import (
    equivalence_ratio,
    stoichiometric_air_fuel_ratio,
    temperature_rise_estimate,
)

# (carbon, hydrogen, oxygen, expected AFR) - reference stoichiometric air-fuel
# ratios from Turns, An Introduction to Combustion, Table 2.1 / standard references.
_AFR_TABLE = [
    (1, 4, 0, 17.2),  # methane, CH4
    (8, 18, 0, 15.1),  # octane (gasoline surrogate), C8H18
    (2, 6, 0, 16.06),  # ethane, C2H6
    (12, 26, 0, 14.98),  # dodecane (jet-fuel surrogate), C12H26
]


@pytest.mark.parametrize("carbon,hydrogen,oxygen,expected_afr", _AFR_TABLE)
def test_stoichiometric_afr_matches_reference_values(
    carbon: int, hydrogen: int, oxygen: int, expected_afr: float
) -> None:
    afr = stoichiometric_air_fuel_ratio(carbon, hydrogen, oxygen)
    assert math.isclose(afr, expected_afr, rel_tol=1e-2)


def test_stoichiometric_afr_methanol_with_oxygen_in_fuel() -> None:
    """Methanol CH3OH -> C1H4O1; the fuel's own oxygen reduces the required air."""
    afr_methanol = stoichiometric_air_fuel_ratio(carbon=1, hydrogen=4, oxygen=1)
    afr_methane = stoichiometric_air_fuel_ratio(carbon=1, hydrogen=4, oxygen=0)
    assert afr_methanol < afr_methane


def test_stoichiometric_afr_rejects_negative_atom_counts() -> None:
    with pytest.raises(InvalidFuelCompositionError):
        stoichiometric_air_fuel_ratio(carbon=-1, hydrogen=4)
    with pytest.raises(InvalidFuelCompositionError):
        stoichiometric_air_fuel_ratio(carbon=1, hydrogen=-4)


def test_stoichiometric_afr_rejects_empty_fuel() -> None:
    with pytest.raises(InvalidFuelCompositionError):
        stoichiometric_air_fuel_ratio(carbon=0, hydrogen=0)


def test_stoichiometric_afr_rejects_fully_oxidized_composition() -> None:
    """CO2 (C1H0O2) has no combustible energy left to release."""
    with pytest.raises(InvalidFuelCompositionError):
        stoichiometric_air_fuel_ratio(carbon=1, hydrogen=0, oxygen=2)


def test_equivalence_ratio_unity_at_stoichiometric() -> None:
    afr_stoich = 17.2
    assert math.isclose(equivalence_ratio(afr_stoich, afr_stoich), 1.0, rel_tol=1e-9)


def test_equivalence_ratio_lean_and_rich() -> None:
    afr_stoich = 17.2
    lean = equivalence_ratio(actual_air_fuel_ratio=20.0, stoichiometric_air_fuel_ratio_=afr_stoich)
    rich = equivalence_ratio(actual_air_fuel_ratio=14.0, stoichiometric_air_fuel_ratio_=afr_stoich)
    assert lean < 1.0  # more air than stoichiometric -> lean
    assert rich > 1.0  # less air than stoichiometric -> rich


def test_equivalence_ratio_rejects_nonpositive_inputs() -> None:
    with pytest.raises(InvalidFuelCompositionError):
        equivalence_ratio(actual_air_fuel_ratio=0, stoichiometric_air_fuel_ratio_=17.2)
    with pytest.raises(InvalidFuelCompositionError):
        equivalence_ratio(actual_air_fuel_ratio=17.2, stoichiometric_air_fuel_ratio_=0)


def test_temperature_rise_matches_energy_balance_formula() -> None:
    mdot_fuel, mdot_air, lhv, cp = 0.5, 25.0, 43e6, 1150.0
    expected = mdot_fuel * lhv / ((mdot_air + mdot_fuel) * cp)
    actual = temperature_rise_estimate(mdot_fuel, mdot_air, lhv, specific_heat=cp)
    assert math.isclose(actual, expected, rel_tol=1e-9)


def test_temperature_rise_scales_with_combustion_efficiency() -> None:
    full = temperature_rise_estimate(0.5, 25.0, 43e6, combustion_efficiency=1.0)
    partial = temperature_rise_estimate(0.5, 25.0, 43e6, combustion_efficiency=0.98)
    assert math.isclose(partial / full, 0.98, rel_tol=1e-9)


def test_temperature_rise_increases_with_fuel_flow() -> None:
    low = temperature_rise_estimate(0.3, 25.0, 43e6)
    high = temperature_rise_estimate(0.6, 25.0, 43e6)
    assert high > low


def test_temperature_rise_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidFuelCompositionError):
        temperature_rise_estimate(0, 25.0, 43e6)
    with pytest.raises(InvalidFuelCompositionError):
        temperature_rise_estimate(0.5, 0, 43e6)
    with pytest.raises(InvalidFuelCompositionError):
        temperature_rise_estimate(0.5, 25.0, 0)
    with pytest.raises(InvalidFuelCompositionError):
        temperature_rise_estimate(0.5, 25.0, 43e6, combustion_efficiency=1.5)
