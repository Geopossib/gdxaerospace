"""plasmaspace — preliminary spacecraft-plasma interaction estimates for GDX Aerospace."""

from __future__ import annotations

from plasmaspace.charging import electron_thermal_flux, floating_potential, ion_bohm_flux
from plasmaspace.exceptions import InvalidSpacePlasmaInputError

__all__ = [
    "InvalidSpacePlasmaInputError",
    "electron_thermal_flux",
    "floating_potential",
    "ion_bohm_flux",
]

__version__ = "0.1.0"
