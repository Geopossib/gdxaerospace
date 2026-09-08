"""Exceptions for combustionpy."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidFuelCompositionError(GDXAerospaceError):
    """Raised when a fuel composition (atom counts) is invalid."""
