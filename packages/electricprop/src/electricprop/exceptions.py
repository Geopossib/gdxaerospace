"""Exceptions for electricprop."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidElectricPropulsionInputError(GDXAerospaceError):
    """Raised when an electric-thruster performance input is physically invalid."""
