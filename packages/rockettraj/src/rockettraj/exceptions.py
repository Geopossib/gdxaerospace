"""Exceptions for rockettraj."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidTrajectoryInputError(GDXAerospaceError):
    """Raised when a rocket trajectory simulation input is physically invalid."""
