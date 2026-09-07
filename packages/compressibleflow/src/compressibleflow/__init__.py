"""compressibleflow — isentropic compressible-flow relations for GDX Aerospace."""

from __future__ import annotations

from compressibleflow.isentropic import (
    GAMMA_AIR,
    area_mach_ratio,
    stagnation_density_ratio,
    stagnation_pressure_ratio,
    stagnation_temperature_ratio,
)

__all__ = [
    "GAMMA_AIR",
    "area_mach_ratio",
    "stagnation_density_ratio",
    "stagnation_pressure_ratio",
    "stagnation_temperature_ratio",
]

__version__ = "0.1.0"
