"""Exceptions for aerovision."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidImageError(GDXAerospaceError):
    """Raised when an input image array is malformed or has an invalid shape."""
