"""Exceptions for plume3d."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidPlumeGeometryError(GDXAerospaceError):
    """Raised when a plume-divergence input is physically invalid."""
