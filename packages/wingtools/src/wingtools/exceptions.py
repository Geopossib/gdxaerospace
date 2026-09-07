"""Exceptions for wingtools."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidWingGeometryError(GDXAerospaceError):
    """Raised when a wing-geometry parameter (AR, efficiency, ...) is out of range."""
