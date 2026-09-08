"""Exceptions for plasmathrust."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidPlasmaParameterError(GDXAerospaceError):
    """Raised when a plasma-parameter input is physically invalid."""
