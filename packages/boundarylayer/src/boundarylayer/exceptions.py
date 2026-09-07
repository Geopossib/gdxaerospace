"""Exceptions for boundarylayer."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidReynoldsNumberError(GDXAerospaceError):
    """Raised when a local Reynolds number is not positive."""

    def __init__(self, reynolds_x: float) -> None:
        message = (
            f"reynolds_x must be positive, got {reynolds_x!r}. "
            "Use aerocalc.reynolds_number(...) with a positive x to compute a valid value."
        )
        super().__init__(message)
        self.reynolds_x = reynolds_x
