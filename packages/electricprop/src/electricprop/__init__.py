"""electricprop — ion and Hall-effect electric thruster performance for GDX Aerospace."""

from __future__ import annotations

from electricprop.exceptions import InvalidElectricPropulsionInputError
from electricprop.ion_acceleration import (
    G0,
    ion_exhaust_velocity,
    specific_impulse_electric,
    thrust_efficiency,
    thrust_from_beam_current,
)
from electricprop.thrusters import ElectrostaticThruster, HallThruster, IonThruster

__all__ = [
    "G0",
    "ElectrostaticThruster",
    "HallThruster",
    "InvalidElectricPropulsionInputError",
    "IonThruster",
    "ion_exhaust_velocity",
    "specific_impulse_electric",
    "thrust_efficiency",
    "thrust_from_beam_current",
]

__version__ = "0.1.0"
