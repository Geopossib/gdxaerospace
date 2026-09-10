"""Exceptions for sparcalc."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidSparInputError(GDXAerospaceError):
    """Raised when a spar/beam analysis input is physically invalid."""
