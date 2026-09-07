"""Exceptions for airfoilpy."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidAirfoilCodeError(GDXAerospaceError):
    """Raised when an airfoil designation string cannot be parsed or is unsupported."""

    def __init__(self, code: str, *, expected: str) -> None:
        message = f"Invalid airfoil code {code!r}: expected {expected}."
        super().__init__(message)
        self.code = code
