"""aerocfd — a Python automation layer around OpenFOAM for GDX Aerospace."""

from __future__ import annotations

from aerocfd.case import OpenFOAMCase
from aerocfd.detect import is_openfoam_available
from aerocfd.exceptions import InvalidCaseError, OpenFOAMNotFoundError
from aerocfd.postprocess import ForceCoefficients, parse_force_coefficients

__all__ = [
    "ForceCoefficients",
    "InvalidCaseError",
    "OpenFOAMCase",
    "OpenFOAMNotFoundError",
    "is_openfoam_available",
    "parse_force_coefficients",
]

__version__ = "0.1.0"
