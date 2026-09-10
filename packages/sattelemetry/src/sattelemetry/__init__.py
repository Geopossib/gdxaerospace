"""sattelemetry — CCSDS-style satellite telemetry for GDX Aerospace."""

from __future__ import annotations

from sattelemetry.archive import TelemetryArchive, TelemetryRecord
from sattelemetry.ccsds import (
    PACKET_TYPE_TC,
    PACKET_TYPE_TM,
    SEQUENCE_FLAG_CONTINUATION,
    SEQUENCE_FLAG_FIRST,
    SEQUENCE_FLAG_LAST,
    SEQUENCE_FLAG_UNSEGMENTED,
    PrimaryHeader,
    pack_primary_header,
    unpack_primary_header,
)
from sattelemetry.channels import RAW_TYPES, TelemetryChannel
from sattelemetry.crc import append_crc, crc16_ccitt, verify_crc
from sattelemetry.decoder import DecodedPacket, PacketLayout, TelemetryDecoder
from sattelemetry.exceptions import ChecksumError, InvalidPacketError, UnknownChannelError
from sattelemetry.limits import ChannelLimits, LimitStatus, check_channels

__all__ = [
    "PACKET_TYPE_TC",
    "PACKET_TYPE_TM",
    "RAW_TYPES",
    "SEQUENCE_FLAG_CONTINUATION",
    "SEQUENCE_FLAG_FIRST",
    "SEQUENCE_FLAG_LAST",
    "SEQUENCE_FLAG_UNSEGMENTED",
    "ChannelLimits",
    "ChecksumError",
    "DecodedPacket",
    "InvalidPacketError",
    "LimitStatus",
    "PacketLayout",
    "PrimaryHeader",
    "TelemetryArchive",
    "TelemetryChannel",
    "TelemetryDecoder",
    "TelemetryRecord",
    "UnknownChannelError",
    "append_crc",
    "check_channels",
    "crc16_ccitt",
    "pack_primary_header",
    "unpack_primary_header",
    "verify_crc",
]

__version__ = "0.1.0"
