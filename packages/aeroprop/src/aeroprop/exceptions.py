"""Exceptions for aeroprop."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidPropulsionInputError(GDXAerospaceError):
    """Raised when a propulsion-performance input is physically invalid."""
