"""Exceptions for tletools."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidTLEError(GDXAerospaceError):
    """Raised when a TLE line is malformed or fails checksum validation."""
