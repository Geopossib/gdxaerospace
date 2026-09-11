"""Exceptions for aerothermal."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidThermalInputError(GDXAerospaceError):
    """Raised when a thermal-analysis input is physically invalid."""
