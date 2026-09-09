"""Exceptions for navigationpy."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidNavigationInputError(GDXAerospaceError):
    """Raised when a navigation input (latitude, longitude, heading) is invalid."""
