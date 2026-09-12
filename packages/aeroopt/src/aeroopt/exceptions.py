"""Exceptions for aeroopt."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class OptimizationError(GDXAerospaceError):
    """Raised when an optimization input is invalid or the underlying solver fails."""
