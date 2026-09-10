"""Exceptions for satprop."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class PropagationError(GDXAerospaceError):
    """Raised when satellite propagation fails (bad TLE, SGP4 internal error, etc.)."""
