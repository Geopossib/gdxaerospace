"""aerothermal — conduction, convection, radiation, and spacecraft thermal balance."""

from __future__ import annotations

from aerothermal.exceptions import InvalidThermalInputError
from aerothermal.heat_transfer import (
    STEFAN_BOLTZMANN_CONSTANT,
    conduction_heat_transfer,
    convection_heat_transfer,
    parallel_resistance,
    radiation_heat_transfer,
    series_resistance,
    thermal_resistance_conduction,
    thermal_resistance_convection,
)
from aerothermal.transient import (
    lumped_capacitance_temperature,
    spacecraft_equilibrium_temperature,
)

__all__ = [
    "STEFAN_BOLTZMANN_CONSTANT",
    "InvalidThermalInputError",
    "conduction_heat_transfer",
    "convection_heat_transfer",
    "lumped_capacitance_temperature",
    "parallel_resistance",
    "radiation_heat_transfer",
    "series_resistance",
    "spacecraft_equilibrium_temperature",
    "thermal_resistance_conduction",
    "thermal_resistance_convection",
]

__version__ = "0.1.0"
