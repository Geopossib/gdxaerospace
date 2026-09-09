"""Exceptions for autopilotpy."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidControllerConfigError(GDXAerospaceError):
    """Raised when a PID controller configuration or input is invalid."""
