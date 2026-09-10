"""Exceptions for fatiguepy."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidFatigueInputError(GDXAerospaceError):
    """Raised when a fatigue-analysis input is physically invalid."""
