"""Exceptions for flightdyn."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidFlightDynamicsInputError(GDXAerospaceError):
    """Raised when a flight-dynamics input (mass, inertia, state vector) is invalid."""
