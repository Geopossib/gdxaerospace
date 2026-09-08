"""plasmathrust — fundamental plasma parameters for GDX Aerospace."""

from __future__ import annotations

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

__all__ = [
    "InvalidPlasmaParameterError",
    "bohm_velocity",
    "debye_length",
    "electron_cyclotron_frequency",
    "hall_parameter",
    "ion_cyclotron_frequency",
    "larmor_radius",
    "plasma_frequency",
]

__version__ = "0.1.0"
