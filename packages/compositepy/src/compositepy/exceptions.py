"""Exceptions for compositepy."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidLaminaError(GDXAerospaceError):
    """Raised when lamina material properties or ply angle are physically invalid."""
