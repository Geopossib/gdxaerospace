"""Exceptions for plasmaspace."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidSpacePlasmaInputError(GDXAerospaceError):
    """Raised when a spacecraft-plasma-interaction input is physically invalid."""
