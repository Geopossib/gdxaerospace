"""groundtrack — coordinate-frame, GMST, and look-angle calculations for GDX Aerospace."""

from __future__ import annotations

from groundtrack.exceptions import InvalidCoordinateError
from groundtrack.geodetic import ecef_to_geodetic, geodetic_to_ecef, look_angles
from groundtrack.time_frames import ecef_to_eci, eci_to_ecef, gmst, julian_date

__all__ = [
    "InvalidCoordinateError",
    "ecef_to_eci",
    "ecef_to_geodetic",
    "eci_to_ecef",
    "geodetic_to_ecef",
    "gmst",
    "julian_date",
    "look_angles",
]

__version__ = "0.1.0"
