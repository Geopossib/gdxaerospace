"""Two-Line Element (TLE) set parsing.

Reference
---------
- Kelso, T.S., "Frequently Asked Questions: Two-Line Element Set Format",
  CelesTrak (the standard public specification of the fixed-column TLE
  format used here, including the assumed-decimal-point and
  exponential-notation field conventions).
- The example/test TLE used throughout this module (ISS, epoch 2008) is
  the standard verification vector from Vallado, D.A. et al.,
  "Revisiting Spacetrack Report #3", AIAA 2006-6753 -- the reference
  test case used by nearly every independent SGP4 implementation.

Convention
----------
- This module parses TLE *text* into structured data (epoch, orbital
  elements, drag terms). It does not propagate the orbit -- for that,
  see ``satprop``, which wraps the ``sgp4`` library.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from tletools.checksum import validate_checksum
from tletools.exceptions import InvalidTLEError


def _parse_decimal_assumed(field: str) -> float:
    """Parse a field like '0006703' (assumed leading '0.') into 0.0006703."""
    field = field.strip()
    if not field:
        raise InvalidTLEError("eccentricity field is empty")
    return float(f"0.{field}")


def _parse_tle_exponential(field: str) -> float:
    """Parse a TLE exponential-notation field like ' 12345-3' or '-11606-4'.

    Format: optional sign, 5 mantissa digits (assumed decimal point
    before them), then a 2-character signed exponent.
    """
    field = field.strip()
    if not field:
        return 0.0
    sign = 1.0
    if field[0] in "+-":
        if field[0] == "-":
            sign = -1.0
        field = field[1:]
    if len(field) < 3:
        raise InvalidTLEError(f"malformed exponential field: {field!r}")
    mantissa_digits, exponent_str = field[:-2], field[-2:]
    mantissa = float(f"0.{mantissa_digits}")
    exponent = int(exponent_str)
    return sign * mantissa * (10.0**exponent)


@dataclass(frozen=True)
class TLEData:
    """Parsed contents of a Two-Line Element set."""

    satellite_number: int
    classification: str
    international_designator: str
    epoch: dt.datetime
    mean_motion_dot: float
    mean_motion_ddot: float
    bstar: float
    element_set_number: int
    inclination_deg: float
    raan_deg: float
    eccentricity: float
    arg_perigee_deg: float
    mean_anomaly_deg: float
    mean_motion_rev_per_day: float
    revolution_number: int


def epoch_to_datetime(epoch_year: int, epoch_day: float) -> dt.datetime:
    """Convert a TLE epoch (2-digit year + fractional day-of-year) to a UTC datetime.

    Parameters
    ----------
    epoch_year:
        2-digit epoch year, 0-99. Per the TLE convention, years 57-99
        mean 1957-1999 and years 0-56 mean 2000-2056 (chosen to bracket
        Sputnik's 1957 launch, the epoch this format predates).
    epoch_day:
        Fractional day of year, >= 1.0 (day 1.0 = January 1st, 00:00 UTC).

    Returns
    -------
    datetime.datetime
        UTC epoch datetime.

    Example
    -------
    >>> epoch_to_datetime(8, 264.51782528)
    datetime.datetime(2008, 9, 20, 12, 25, 40, 104192)

    """
    full_year = 1900 + epoch_year if epoch_year >= 57 else 2000 + epoch_year
    return dt.datetime(full_year, 1, 1) + dt.timedelta(days=epoch_day - 1)


def parse_tle(line1: str, line2: str, *, validate: bool = True) -> TLEData:
    """Parse a two-line element set into structured orbital data.

    Parameters
    ----------
    line1, line2:
        The two TLE lines, each at least 69 characters.
    validate:
        If True (default), validate both lines' checksums and raise
        :class:`InvalidTLEError` if either fails.

    Returns
    -------
    TLEData

    Raises
    ------
    InvalidTLEError
        If the lines are malformed, mismatched (different satellite
        numbers), or fail checksum validation.

    Example
    -------
    >>> line1 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
    >>> line2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
    >>> tle = parse_tle(line1, line2)
    >>> tle.satellite_number
    25544
    >>> tle.inclination_deg
    51.6416
    >>> round(tle.bstar, 10)
    -1.1606e-05

    """
    if len(line1) < 69 or len(line2) < 69:
        raise InvalidTLEError("both TLE lines must be at least 69 characters")
    if line1[0] != "1" or line2[0] != "2":
        raise InvalidTLEError("line1 must start with '1' and line2 must start with '2'")

    if validate:
        if not validate_checksum(line1):
            raise InvalidTLEError("line1 fails checksum validation")
        if not validate_checksum(line2):
            raise InvalidTLEError("line2 fails checksum validation")

    sat_num_1 = line1[2:7].strip()
    sat_num_2 = line2[2:7].strip()
    if sat_num_1 != sat_num_2:
        raise InvalidTLEError(
            f"satellite number mismatch between lines: {sat_num_1!r} vs {sat_num_2!r}"
        )

    epoch_year = int(line1[18:20])
    epoch_day = float(line1[20:32])

    return TLEData(
        satellite_number=int(sat_num_1),
        classification=line1[7],
        international_designator=line1[9:17].strip(),
        epoch=epoch_to_datetime(epoch_year, epoch_day),
        mean_motion_dot=float(line1[33:43]),
        mean_motion_ddot=_parse_tle_exponential(line1[44:52]),
        bstar=_parse_tle_exponential(line1[53:61]),
        element_set_number=int(line1[64:68].strip()),
        inclination_deg=float(line2[8:16]),
        raan_deg=float(line2[17:25]),
        eccentricity=_parse_decimal_assumed(line2[26:33]),
        arg_perigee_deg=float(line2[34:42]),
        mean_anomaly_deg=float(line2[43:51]),
        mean_motion_rev_per_day=float(line2[52:63]),
        revolution_number=int(line2[63:68].strip()),
    )
