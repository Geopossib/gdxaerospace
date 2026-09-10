"""Exceptions for aeromaterials."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class UnknownMaterialError(GDXAerospaceError):
    """Raised when a requested material name is not in the database."""
