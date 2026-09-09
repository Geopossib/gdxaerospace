"""Exceptions for guidancepy."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidGuidanceInputError(GDXAerospaceError):
    """Raised when a guidance-law input is physically invalid."""
