"""CRC-16/CCITT-FALSE checksum, a common telemetry frame integrity check.

Reference
---------
- Koopman, P. & Chakravarty, T., "Cyclic Redundancy Code (CRC)
  Polynomial Selection For Embedded Networks", DSN 2004 (CRC design
  background).
- This is the CRC-16/CCITT-FALSE variant: polynomial 0x1021, initial
  value 0xFFFF, no input/output reflection, no final XOR. It is one of
  the most common CRC-16 variants used in space and embedded telemetry
  protocols. Its standard check value -- the CRC of the ASCII string
  "123456789" -- is 0x29B1, per the CRC RevEng catalogue
  (reveng.sourceforge.io/crc-catalogue), and is used here as the
  module's own correctness test.

Assumptions
-----------
- This module implements exactly one CRC-16 variant (CCITT-FALSE).
  Telemetry systems in the wild use several different CRC-16 parameter
  sets that all get casually called "CRC-16-CCITT" despite giving
  different results (reflected vs non-reflected, different init values)
  -- always confirm which exact variant a real mission's ICD specifies
  before assuming this one matches.
"""

from __future__ import annotations

_POLYNOMIAL = 0x1021
_INITIAL_VALUE = 0xFFFF


def crc16_ccitt(data: bytes) -> int:
    """Compute the CRC-16/CCITT-FALSE checksum of ``data``.

    Parameters
    ----------
    data:
        Bytes to checksum.

    Returns
    -------
    int
        16-bit CRC value, 0-65535.

    Example
    -------
    The standard CRC-16/CCITT-FALSE check value for the ASCII string
    "123456789" is 0x29B1 (from the CRC RevEng catalogue):

    >>> hex(crc16_ccitt(b"123456789"))
    '0x29b1'

    """
    crc = _INITIAL_VALUE
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ _POLYNOMIAL) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def append_crc(data: bytes) -> bytes:
    """Append a big-endian CRC-16/CCITT-FALSE checksum to ``data``.

    Parameters
    ----------
    data:
        Bytes to checksum and append to.

    Returns
    -------
    bytes
        ``data`` followed by 2 big-endian CRC bytes.

    Example
    -------
    >>> append_crc(b"123456789").hex()
    '31323334353637383929b1'

    """
    crc = crc16_ccitt(data)
    return data + crc.to_bytes(2, "big")


def verify_crc(data_with_crc: bytes) -> bool:
    r"""Verify that the last 2 bytes of ``data_with_crc`` are its correct CRC.

    Parameters
    ----------
    data_with_crc:
        Data followed by a 2-byte big-endian CRC-16/CCITT-FALSE
        checksum, as produced by :func:`append_crc`. Must be at least 2
        bytes long.

    Returns
    -------
    bool
        True if the trailing CRC matches the checksum of the preceding
        bytes.

    Example
    -------
    >>> verify_crc(append_crc(b"123456789"))
    True
    >>> verify_crc(b"123456789" + b"\\x00\\x00")
    False

    """
    if len(data_with_crc) < 2:
        return False
    payload, crc_bytes = data_with_crc[:-2], data_with_crc[-2:]
    expected = int.from_bytes(crc_bytes, "big")
    return crc16_ccitt(payload) == expected
