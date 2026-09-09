"""flightdyn — rigid-body 6-DOF flight dynamics equations of motion for GDX Aerospace."""

from __future__ import annotations

from flightdyn.exceptions import InvalidFlightDynamicsInputError
from flightdyn.rigid_body import (
    G0,
    gravity_body_frame,
    position_derivative,
    rotational_acceleration,
    translational_acceleration,
)

__all__ = [
    "G0",
    "InvalidFlightDynamicsInputError",
    "gravity_body_frame",
    "position_derivative",
    "rotational_acceleration",
    "translational_acceleration",
]

__version__ = "0.1.0"
