"""combustionpy — combustion stoichiometry and simplified thermochemistry for GDX Aerospace."""

from __future__ import annotations

from combustionpy.exceptions import InvalidFuelCompositionError
from combustionpy.stoichiometry import (
    equivalence_ratio,
    stoichiometric_air_fuel_ratio,
    temperature_rise_estimate,
)

__all__ = [
    "InvalidFuelCompositionError",
    "equivalence_ratio",
    "stoichiometric_air_fuel_ratio",
    "temperature_rise_estimate",
]

__version__ = "0.1.0"
