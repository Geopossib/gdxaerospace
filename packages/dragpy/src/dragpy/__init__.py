"""dragpy — skin-friction and parasitic drag estimation for GDX Aerospace."""

from __future__ import annotations

from dragpy.exceptions import InvalidDragModelError
from dragpy.parasite_drag import DragComponent, ParasiteDragBuildup
from dragpy.skin_friction import (
    skin_friction_coefficient_laminar,
    skin_friction_coefficient_turbulent,
)

__all__ = [
    "DragComponent",
    "InvalidDragModelError",
    "ParasiteDragBuildup",
    "skin_friction_coefficient_laminar",
    "skin_friction_coefficient_turbulent",
]

__version__ = "0.1.0"
