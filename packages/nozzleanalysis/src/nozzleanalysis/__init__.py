"""nozzleanalysis — isentropic rocket/jet nozzle flow analysis for GDX Aerospace."""

from __future__ import annotations

from nozzleanalysis.exceptions import InvalidNozzleInputError
from nozzleanalysis.nozzle_flow import (
    choked_mass_flow,
    exit_mach_from_area_ratio,
    nozzle_exit_conditions,
)

__all__ = [
    "InvalidNozzleInputError",
    "choked_mass_flow",
    "exit_mach_from_area_ratio",
    "nozzle_exit_conditions",
]

__version__ = "0.1.0"
