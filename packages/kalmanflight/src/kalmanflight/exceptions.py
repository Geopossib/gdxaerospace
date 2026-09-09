"""Exceptions for kalmanflight."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidKalmanFilterInputError(GDXAerospaceError):
    """Raised when a Kalman filter matrix/vector input has an invalid shape or value."""
