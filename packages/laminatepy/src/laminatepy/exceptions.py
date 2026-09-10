"""Exceptions for laminatepy."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidLaminateError(GDXAerospaceError):
    """Raised when a laminate ply stack or load input is physically invalid."""
