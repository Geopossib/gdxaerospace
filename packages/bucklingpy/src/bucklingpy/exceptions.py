"""Exceptions for bucklingpy."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidBucklingInputError(GDXAerospaceError):
    """Raised when a buckling-analysis input is physically invalid."""
