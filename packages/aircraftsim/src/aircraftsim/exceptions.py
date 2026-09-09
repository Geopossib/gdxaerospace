"""Exceptions for aircraftsim."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidAircraftConfigError(GDXAerospaceError):
    """Raised when an Aircraft6DOF configuration or control input is invalid."""
