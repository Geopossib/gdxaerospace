"""aircraftsim — a simple 6-DOF aircraft flight simulator for GDX Aerospace."""

from __future__ import annotations

from aircraftsim.aero_model import LinearAeroModel
from aircraftsim.aircraft6dof import Aircraft6DOF
from aircraftsim.exceptions import InvalidAircraftConfigError

__all__ = [
    "Aircraft6DOF",
    "InvalidAircraftConfigError",
    "LinearAeroModel",
]

__version__ = "0.1.0"
