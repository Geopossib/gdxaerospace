"""plume3d — simplified plume-divergence loss estimation for GDX Aerospace."""

from __future__ import annotations

from plume3d.divergence import (
    divergence_thrust_correction,
    effective_specific_impulse,
    effective_thrust,
    half_angle_from_correction,
)
from plume3d.exceptions import InvalidPlumeGeometryError

__all__ = [
    "InvalidPlumeGeometryError",
    "divergence_thrust_correction",
    "effective_specific_impulse",
    "effective_thrust",
    "half_angle_from_correction",
]

__version__ = "0.1.0"
