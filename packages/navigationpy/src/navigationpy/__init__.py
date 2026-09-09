"""navigationpy — great-circle navigation and dead reckoning for GDX Aerospace."""

from __future__ import annotations

from navigationpy.exceptions import InvalidNavigationInputError
from navigationpy.great_circle import (
    EARTH_RADIUS,
    dead_reckon,
    great_circle_distance,
    initial_bearing,
)

__all__ = [
    "EARTH_RADIUS",
    "InvalidNavigationInputError",
    "dead_reckon",
    "great_circle_distance",
    "initial_bearing",
]

__version__ = "0.1.0"
