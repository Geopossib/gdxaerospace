"""Telemetry channel definitions and raw-to-engineering-unit calibration.

Reference
---------
- Consultative Committee for Space Data Systems (CCSDS) and most flight
  telemetry systems represent each measured quantity as a "channel"
  with: a location in the packet's data field, a raw data type, and a
  calibration curve to convert the raw sensor reading into engineering
  units. Polynomial calibration curves (the most common form) are
  covered here; lookup-table calibration (common for thermistors and
  other nonlinear sensors) is intentionally out of scope for this first
  version.

Convention
----------
- A channel's raw value is extracted from a packet as a fixed-width,
  big-endian field at a known byte offset (see
  :mod:`sattelemetry.decoder`), then converted via
  :meth:`TelemetryChannel.to_engineering_units`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sattelemetry.exceptions import InvalidPacketError

#: Supported raw field types and their (struct format char, byte width).
RAW_TYPES = {
    "u8": ("B", 1),
    "u16": ("H", 2),
    "u32": ("I", 4),
    "i8": ("b", 1),
    "i16": ("h", 2),
    "i32": ("i", 4),
    "f32": ("f", 4),
}


@dataclass(frozen=True)
class TelemetryChannel:
    """One telemetry channel: where to find it in a packet and how to calibrate it.

    Parameters
    ----------
    name:
        Channel name (e.g. ``"battery_voltage"``).
    byte_offset:
        Byte offset of this channel's raw field within the packet's data
        field (not including the primary header), >= 0.
    raw_type:
        One of the keys in :data:`RAW_TYPES` (``"u8"``, ``"u16"``,
        ``"u32"``, ``"i8"``, ``"i16"``, ``"i32"``, ``"f32"``).
    units:
        Engineering units label (e.g. ``"V"``, ``"degC"``), for display
        only.
    polynomial_coefficients:
        Coefficients ``[c0, c1, c2, ...]`` such that
        ``engineering_value = c0 + c1*raw + c2*raw^2 + ...``. Defaults
        to ``[0.0, 1.0]`` (identity: engineering value equals raw value).

    """

    name: str
    byte_offset: int
    raw_type: str
    units: str = ""
    polynomial_coefficients: tuple[float, ...] = field(default=(0.0, 1.0))

    def __post_init__(self) -> None:
        if self.byte_offset < 0:
            raise InvalidPacketError(
                f"byte_offset must be non-negative, got {self.byte_offset!r}"
            )
        if self.raw_type not in RAW_TYPES:
            valid = ", ".join(sorted(RAW_TYPES))
            raise InvalidPacketError(
                f"raw_type {self.raw_type!r} is not supported; expected one of: {valid}"
            )
        if len(self.polynomial_coefficients) == 0:
            raise InvalidPacketError("polynomial_coefficients must not be empty")

    @property
    def byte_width(self) -> int:
        """Width of this channel's raw field, in bytes."""
        return RAW_TYPES[self.raw_type][1]

    def to_engineering_units(self, raw_value: float) -> float:
        """Apply the polynomial calibration curve to a raw value.

        Parameters
        ----------
        raw_value:
            Raw (uncalibrated) sensor reading.

        Returns
        -------
        float
            Calibrated value in engineering units.

        Example
        -------
        A channel that converts a raw ADC count (0-4095) to volts
        (0-5 V) via a linear calibration:

        >>> channel = TelemetryChannel(
        ...     "battery_voltage", byte_offset=0, raw_type="u16",
        ...     units="V", polynomial_coefficients=(0.0, 5.0 / 4095.0),
        ... )
        >>> round(channel.to_engineering_units(2048), 4)
        2.5006

        """
        return sum(
            coeff * raw_value**power
            for power, coeff in enumerate(self.polynomial_coefficients)
        )
