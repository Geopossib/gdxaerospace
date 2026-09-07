"""aerocalc — core atmospheric and flow-property calculations.

Part of the GDX Aerospace ecosystem. See the package README and
``docs/`` for equations, assumptions, and references.
"""

from __future__ import annotations

from aerocalc.atmosphere import Atmosphere, AtmosphereState
from aerocalc.exceptions import (
    GDXAerospaceError,
    InvalidAltitudeError,
    InvalidMachNumberError,
    SimulationConvergenceError,
    UnitConversionError,
)
from aerocalc.flow import (
    dynamic_pressure,
    mach_number,
    reynolds_number,
    sutherland_viscosity,
)

__all__ = [
    "Atmosphere",
    "AtmosphereState",
    "GDXAerospaceError",
    "InvalidAltitudeError",
    "InvalidMachNumberError",
    "SimulationConvergenceError",
    "UnitConversionError",
    "dynamic_pressure",
    "mach_number",
    "reynolds_number",
    "sutherland_viscosity",
]

__version__ = "0.1.0"
