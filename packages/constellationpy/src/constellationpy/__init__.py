"""constellationpy — Walker constellation geometry and coverage analysis for GDX Aerospace."""

from __future__ import annotations

from constellationpy.exceptions import InvalidConstellationError
from constellationpy.walker import (
    SatelliteSlot,
    coverage_ground_range,
    coverage_half_angle,
    walker_constellation,
)

__all__ = [
    "InvalidConstellationError",
    "SatelliteSlot",
    "coverage_ground_range",
    "coverage_half_angle",
    "walker_constellation",
]

__version__ = "0.1.0"
