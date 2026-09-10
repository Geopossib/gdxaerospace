"""Exceptions for constellationpy."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidConstellationError(GDXAerospaceError):
    """Raised when a constellation-pattern or coverage-geometry input is invalid."""
