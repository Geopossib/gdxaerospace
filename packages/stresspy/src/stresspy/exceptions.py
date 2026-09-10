"""Exceptions for stresspy."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidStressInputError(GDXAerospaceError):
    """Raised when a stress/strain calculation input is physically invalid."""
