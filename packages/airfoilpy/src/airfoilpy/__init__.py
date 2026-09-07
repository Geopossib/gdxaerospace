"""airfoilpy — NACA airfoil geometry generation for GDX Aerospace."""

from __future__ import annotations

from airfoilpy.exceptions import InvalidAirfoilCodeError
from airfoilpy.naca4 import AirfoilCoordinates, naca4_camber, naca4_coordinates, naca4_thickness
from airfoilpy.naca5 import naca5_camber, naca5_coordinates

__all__ = [
    "AirfoilCoordinates",
    "InvalidAirfoilCodeError",
    "naca4_camber",
    "naca4_coordinates",
    "naca4_thickness",
    "naca5_camber",
    "naca5_coordinates",
]

__version__ = "0.1.0"
