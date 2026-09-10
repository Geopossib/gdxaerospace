"""Exceptions for orbitpy."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidOrbitError(GDXAerospaceError):
    """Raised when an orbital element or state vector is physically invalid."""


class OrbitSolverConvergenceError(GDXAerospaceError):
    """Raised when an iterative orbital solver (e.g. Kepler's equation) fails to converge."""

    def __init__(self, routine: str, iterations: int, tolerance: float) -> None:
        message = (
            f"'{routine}' failed to converge after {iterations} iterations "
            f"to tolerance {tolerance:.2e}."
        )
        super().__init__(message)
