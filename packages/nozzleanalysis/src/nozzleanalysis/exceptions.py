"""Exceptions for nozzleanalysis."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidNozzleInputError(GDXAerospaceError):
    """Raised when a nozzle-flow input is physically invalid."""
