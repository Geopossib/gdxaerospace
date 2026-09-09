"""Exceptions for attitude3d."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidAttitudeInputError(GDXAerospaceError):
    """Raised for an invalid attitude-representation input (bad shape, non-unit quaternion)."""
