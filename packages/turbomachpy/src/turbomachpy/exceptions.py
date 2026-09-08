"""Exceptions for turbomachpy."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidTurbomachineryInputError(GDXAerospaceError):
    """Raised when a turbine/compressor stage input is physically invalid."""
