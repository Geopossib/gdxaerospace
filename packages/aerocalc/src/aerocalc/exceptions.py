"""Shared exception hierarchy for GDX Aerospace's ``aerocalc`` package.

Every exception here is intended to be raised with a message that tells the
caller *how* to fix their input — not just that it was wrong. Other GDX
Aerospace packages (e.g. ``shockpy``, ``dragpy``) subclass
:class:`GDXAerospaceError` for their own domain-specific errors so that
downstream code can catch the whole ecosystem's errors with one class if
needed.
"""

from __future__ import annotations


class GDXAerospaceError(Exception):
    """Base class for all GDX Aerospace ecosystem errors."""


class InvalidAltitudeError(GDXAerospaceError):
    """Raised when an altitude is outside the range a model supports.

    Parameters
    ----------
    altitude:
        The offending altitude, in meters.
    valid_range:
        The ``(min, max)`` altitude in meters that the model supports.
    model:
        Name of the model/layer that rejected the altitude.

    """

    def __init__(
        self, altitude: float, valid_range: tuple[float, float], model: str
    ) -> None:
        low, high = valid_range
        message = (
            f"Altitude {altitude:.1f} m is outside the range supported by "
            f"the '{model}' model ({low:.1f} m to {high:.1f} m). "
            "Use a different model, or pass an altitude within this range."
        )
        super().__init__(message)
        self.altitude = altitude
        self.valid_range = valid_range
        self.model = model


class InvalidMachNumberError(GDXAerospaceError):
    """Raised when a Mach number is invalid (e.g. negative) for a calculation."""

    def __init__(self, mach: float, reason: str) -> None:
        message = f"Invalid Mach number {mach!r}: {reason}"
        super().__init__(message)
        self.mach = mach


class UnitConversionError(GDXAerospaceError):
    """Raised when a quantity cannot be converted to the units a function expects."""

    def __init__(self, value: object, expected_dimensionality: str) -> None:
        message = (
            f"Could not interpret {value!r} as a quantity with dimensionality "
            f"'{expected_dimensionality}'. Pass a plain number in SI units, "
            "or an aerounits.Q_ quantity with compatible units."
        )
        super().__init__(message)


class SimulationConvergenceError(GDXAerospaceError):
    """Raised when an iterative numerical routine fails to converge."""

    def __init__(self, routine: str, iterations: int, tolerance: float) -> None:
        message = (
            f"'{routine}' failed to converge after {iterations} iterations "
            f"to tolerance {tolerance:.2e}. Try relaxing the tolerance, "
            "increasing max_iterations, or checking the input for physical "
            "validity."
        )
        super().__init__(message)
