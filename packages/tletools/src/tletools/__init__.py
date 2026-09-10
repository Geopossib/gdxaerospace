"""tletools — Two-Line Element (TLE) set parsing and validation for GDX Aerospace."""

from __future__ import annotations

from tletools.checksum import compute_checksum, validate_checksum
from tletools.exceptions import InvalidTLEError
from tletools.parser import TLEData, epoch_to_datetime, parse_tle

__all__ = [
    "InvalidTLEError",
    "TLEData",
    "compute_checksum",
    "epoch_to_datetime",
    "parse_tle",
    "validate_checksum",
]

__version__ = "0.1.0"
