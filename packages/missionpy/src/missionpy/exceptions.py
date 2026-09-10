"""Exceptions for missionpy."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidMissionInputError(GDXAerospaceError):
    """Raised when a mission-analysis input is physically invalid."""
