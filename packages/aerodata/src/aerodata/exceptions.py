"""Exceptions for aerodata."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidFlightDataError(GDXAerospaceError):
    """Raised when a flight-test/telemetry data analysis input is invalid."""
