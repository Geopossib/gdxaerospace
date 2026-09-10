"""CCSDS Space Packet Protocol primary header pack/unpack.

Reference
---------
- CCSDS 133.0-B-2, *Space Packet Protocol*, Blue Book, Consultative
  Committee for Space Data Systems, Ch. 4 (primary header field
  definitions and bit widths).

Convention
----------
- The primary header is exactly 6 octets, transmitted big-endian
  (network byte order), as three 16-bit words:

  Word 1 (16 bits): version (3) | type (1) | secondary_header_flag (1) | apid (11)
  Word 2 (16 bits): sequence_flags (2) | sequence_count (14)
  Word 3 (16 bits): packet_data_length (16) -- stores (data length in
  octets) - 1, per the standard's own convention, so a packet with a
  zero-length data field is still representable.
- This module covers only the primary header. CCSDS also defines an
  optional secondary header (mission-specific format, e.g. a CCSDS Day
  Segmented time code) which is not standardized enough to give a single
  implementation here -- see ``sattelemetry.decoder`` for how a specific
  mission's packet layout (including any secondary header fields) is
  described and decoded.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

from sattelemetry.exceptions import InvalidPacketError

_HEADER_LENGTH = 6

#: Packet type: telemetry (TM).
PACKET_TYPE_TM = 0
#: Packet type: telecommand (TC).
PACKET_TYPE_TC = 1

#: Sequence flags: continuation segment of a segmented packet group.
SEQUENCE_FLAG_CONTINUATION = 0
#: Sequence flags: first segment of a segmented packet group.
SEQUENCE_FLAG_FIRST = 1
#: Sequence flags: last segment of a segmented packet group.
SEQUENCE_FLAG_LAST = 2
#: Sequence flags: packet is not part of a segmented group (the common case).
SEQUENCE_FLAG_UNSEGMENTED = 3


@dataclass(frozen=True)
class PrimaryHeader:
    """A decoded CCSDS Space Packet primary header."""

    version: int
    packet_type: int
    secondary_header_flag: bool
    apid: int
    sequence_flags: int
    sequence_count: int
    data_length: int
    """Length of the packet data field, in octets (already un-biased from
    the on-wire (length - 1) encoding)."""


def pack_primary_header(
    apid: int,
    data_length: int,
    *,
    packet_type: int = PACKET_TYPE_TM,
    secondary_header_flag: bool = False,
    sequence_flags: int = SEQUENCE_FLAG_UNSEGMENTED,
    sequence_count: int = 0,
    version: int = 0,
) -> bytes:
    """Pack a CCSDS Space Packet primary header into 6 bytes.

    Parameters
    ----------
    apid:
        Application Process ID, 0-2047 (11 bits).
    data_length:
        Length of the packet data field, in octets, 1-65536 (the header
        internally stores ``data_length - 1``, per the standard).
    packet_type:
        :data:`PACKET_TYPE_TM` (0) or :data:`PACKET_TYPE_TC` (1).
    secondary_header_flag:
        Whether a secondary header follows the primary header.
    sequence_flags:
        0-3: continuation, first, last, or unsegmented (default: 3,
        unsegmented -- the packet is not part of a larger segmented group).
    sequence_count:
        Packet sequence count, 0-16383 (14 bits).
    version:
        CCSDS packet version number, 0-7 (3 bits); always 0 for current
        CCSDS packets.

    Returns
    -------
    bytes
        6-byte packed primary header.

    Example
    -------
    >>> header = pack_primary_header(apid=100, data_length=10, sequence_count=42)
    >>> len(header)
    6
    >>> unpack_primary_header(header).apid
    100

    """
    if not (0 <= apid <= 0x7FF):
        raise InvalidPacketError(f"apid must be in [0, 2047], got {apid!r}")
    if not (1 <= data_length <= 65536):
        raise InvalidPacketError(f"data_length must be in [1, 65536], got {data_length!r}")
    if packet_type not in (PACKET_TYPE_TM, PACKET_TYPE_TC):
        raise InvalidPacketError(f"packet_type must be 0 or 1, got {packet_type!r}")
    if not (0 <= sequence_flags <= 3):
        raise InvalidPacketError(f"sequence_flags must be in [0, 3], got {sequence_flags!r}")
    if not (0 <= sequence_count <= 0x3FFF):
        raise InvalidPacketError(
            f"sequence_count must be in [0, 16383], got {sequence_count!r}"
        )
    if not (0 <= version <= 7):
        raise InvalidPacketError(f"version must be in [0, 7], got {version!r}")

    word1 = (version << 13) | (packet_type << 12) | (int(secondary_header_flag) << 11) | apid
    word2 = (sequence_flags << 14) | sequence_count
    word3 = data_length - 1
    return struct.pack(">HHH", word1, word2, word3)


def unpack_primary_header(data: bytes) -> PrimaryHeader:
    """Unpack the first 6 bytes of ``data`` as a CCSDS primary header.

    Parameters
    ----------
    data:
        At least 6 bytes; only the first 6 are read.

    Returns
    -------
    PrimaryHeader

    Raises
    ------
    InvalidPacketError
        If ``data`` is shorter than 6 bytes.

    Example
    -------
    >>> header = pack_primary_header(apid=100, data_length=10, sequence_count=42)
    >>> h = unpack_primary_header(header)
    >>> h.apid, h.sequence_count, h.data_length
    (100, 42, 10)

    """
    if len(data) < _HEADER_LENGTH:
        raise InvalidPacketError(
            f"data must be at least {_HEADER_LENGTH} bytes for a primary header, "
            f"got {len(data)}"
        )
    word1, word2, word3 = struct.unpack(">HHH", data[:_HEADER_LENGTH])
    return PrimaryHeader(
        version=(word1 >> 13) & 0x7,
        packet_type=(word1 >> 12) & 0x1,
        secondary_header_flag=bool((word1 >> 11) & 0x1),
        apid=word1 & 0x7FF,
        sequence_flags=(word2 >> 14) & 0x3,
        sequence_count=word2 & 0x3FFF,
        data_length=word3 + 1,
    )
