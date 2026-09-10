"""Exceptions for sattelemetry."""

from __future__ import annotations

from aerocalc.exceptions import GDXAerospaceError


class InvalidPacketError(GDXAerospaceError):
    """Raised when a telemetry packet is malformed, too short, or fails validation."""


class ChecksumError(GDXAerospaceError):
    """Raised when a packet's CRC does not match its computed checksum."""


class UnknownChannelError(GDXAerospaceError):
    """Raised when a requested telemetry channel is not defined in a packet layout."""
