"""Exceptions for uavpy."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidUAVInputError(GDXAerospaceError):
    """Raised when a UAV sizing/performance input is physically invalid."""
