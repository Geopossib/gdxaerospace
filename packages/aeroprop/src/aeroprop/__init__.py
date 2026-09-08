"""aeroprop — general air-breathing propulsion performance relations."""

from __future__ import annotations

from aeroprop.exceptions import InvalidPropulsionInputError
from aeroprop.thrust import (
    G0,
    propulsive_efficiency,
    specific_impulse,
    thrust_airbreathing,
    thrust_specific_fuel_consumption,
)

__all__ = [
    "G0",
    "InvalidPropulsionInputError",
    "propulsive_efficiency",
    "specific_impulse",
    "thrust_airbreathing",
    "thrust_specific_fuel_consumption",
]

__version__ = "0.1.0"
