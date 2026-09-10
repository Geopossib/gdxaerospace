"""Exceptions for aerostruct."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidSectionError(GDXAerospaceError):
    """Raised when a cross-section's geometric parameters are physically invalid."""
