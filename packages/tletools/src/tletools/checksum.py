"""TLE line checksum computation and validation.

Reference
---------
- Kelso, T.S., "Frequently Asked Questions: Two-Line Element Set Format",
  CelesTrak (the standard public specification of the NORAD/Space-Track
  TLE format, including the checksum algorithm).

Convention
----------
- The checksum is computed over the first 68 characters of a TLE line
  (columns 1-68): each digit contributes its value, each ``-`` counts as
  1, and every other character (letters, ``+``, ``.``, spaces) counts as
  0. The result mod 10 must equal the checksum digit in column 69.
"""

from __future__ import annotations

from tletools.exceptions import InvalidTLEError


def compute_checksum(line: str) -> int:
    """Compute the TLE checksum digit for the first 68 characters of a line.

    Parameters
    ----------
    line:
        A TLE line, at least 68 characters long (the checksum digit
        itself, if present at column 69, is ignored).

    Returns
    -------
    int
        Checksum digit, 0-9.

    Example
    -------
    >>> compute_checksum("1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2926")
    7

    """
    if len(line) < 68:
        raise InvalidTLEError(f"line must be at least 68 characters, got {len(line)}")
    total = 0
    for char in line[:68]:
        if char.isdigit():
            total += int(char)
        elif char == "-":
            total += 1
    return total % 10


def validate_checksum(line: str) -> bool:
    """Check whether a TLE line's checksum digit (column 69) matches its content.

    Parameters
    ----------
    line:
        A full TLE line, at least 69 characters long.

    Returns
    -------
    bool
        True if the checksum matches.

    Example
    -------
    >>> validate_checksum("1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927")
    True

    """
    if len(line) < 69:
        raise InvalidTLEError(f"line must be at least 69 characters, got {len(line)}")
    expected = compute_checksum(line)
    actual_char = line[68]
    if not actual_char.isdigit():
        raise InvalidTLEError(f"checksum character at column 69 is not a digit: {actual_char!r}")
    return expected == int(actual_char)
