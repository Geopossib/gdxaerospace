"""Exceptions for groundtrack."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidCoordinateError(GDXAerospaceError):
    """Raised when a coordinate/time input is physically invalid."""
