"""Exceptions for rocketperf."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidRocketInputError(GDXAerospaceError):
    """Raised when a rocket-performance input is physically invalid."""
