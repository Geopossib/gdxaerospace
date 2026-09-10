"""Decode raw telemetry packets into named, calibrated channel values.

Reference
---------
- Combines :mod:`sattelemetry.ccsds` (primary header), an optional CRC
  trailer (:mod:`sattelemetry.crc`), and a list of
  :class:`~sattelemetry.channels.TelemetryChannel` definitions (a
  "packet layout") into a single decode step -- the same overall
  structure real ground-station decode software uses (parse header,
  validate, extract fields, calibrate).

Convention
----------
- A packet on the wire is: 6-byte CCSDS primary header, then the data
  field (channel bytes), then optionally a 2-byte trailing CRC. Whether
  a CRC trailer is present is a property of the packet layout, not
  something auto-detected from the bytes.
- The CRC, when present, is computed over the data field ONLY (not the
  6-byte primary header) -- the same convention used by the ECSS
  Packet Utilization Standard (PUS) and many small-satellite missions.
  Some missions instead checksum the full packet including the header;
  confirm which convention a real mission's ICD specifies before
  assuming this one matches.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field

from sattelemetry.ccsds import PrimaryHeader, unpack_primary_header
from sattelemetry.channels import RAW_TYPES, TelemetryChannel
from sattelemetry.crc import verify_crc
from sattelemetry.exceptions import ChecksumError, InvalidPacketError, UnknownChannelError


@dataclass(frozen=True)
class PacketLayout:
    """A named set of channels describing one packet type (identified by APID).

    Parameters
    ----------
    name:
        Layout name, for reference (e.g. ``"housekeeping"``).
    apid:
        Expected CCSDS Application Process ID for packets of this layout.
    channels:
        The channels present in this packet's data field.
    has_crc:
        Whether packets of this layout end with a 2-byte CRC-16/CCITT
        trailer (see :mod:`sattelemetry.crc`).

    """

    name: str
    apid: int
    channels: tuple[TelemetryChannel, ...] = field(default_factory=tuple)
    has_crc: bool = True

    def channel(self, name: str) -> TelemetryChannel:
        """Look up a channel by name.

        Raises
        ------
        UnknownChannelError
            If no channel with this name is defined in the layout.

        """
        for ch in self.channels:
            if ch.name == name:
                return ch
        raise UnknownChannelError(
            f"no channel named {name!r} in layout {self.name!r}; "
            f"available channels: {[c.name for c in self.channels]}"
        )


@dataclass(frozen=True)
class DecodedPacket:
    """The result of decoding one telemetry packet."""

    header: PrimaryHeader
    layout_name: str
    values: dict[str, float]
    """Calibrated (engineering-unit) value for each channel, by name."""
    raw_values: dict[str, int | float]
    """Uncalibrated raw value for each channel, by name."""


class TelemetryDecoder:
    """Decode raw packet bytes according to a set of registered packet layouts.

    Parameters
    ----------
    layouts:
        Packet layouts this decoder knows how to interpret, keyed by
        their APID internally (so each APID must be unique across the
        registered layouts).

    """

    def __init__(self, layouts: list[PacketLayout]) -> None:
        self._layouts_by_apid: dict[int, PacketLayout] = {}
        for layout in layouts:
            if layout.apid in self._layouts_by_apid:
                raise InvalidPacketError(
                    f"duplicate APID {layout.apid} between layouts "
                    f"{self._layouts_by_apid[layout.apid].name!r} and {layout.name!r}"
                )
            self._layouts_by_apid[layout.apid] = layout

    def decode(self, raw_packet: bytes, *, verify_checksum: bool = True) -> DecodedPacket:
        """Decode one raw packet: header, checksum, and calibrated channel values.

        Parameters
        ----------
        raw_packet:
            Full packet bytes: 6-byte primary header, data field, and
            (if the matched layout specifies ``has_crc=True``) a
            trailing 2-byte CRC.
        verify_checksum:
            If True (default) and the matched layout has a CRC trailer,
            verify it and raise :class:`ChecksumError` on mismatch.

        Returns
        -------
        DecodedPacket

        Raises
        ------
        InvalidPacketError
            If the packet is too short, its declared length doesn't
            match the actual data present, or its APID has no
            registered layout.
        ChecksumError
            If checksum verification is requested and fails.

        Example
        -------
        >>> import struct
        >>> from sattelemetry.ccsds import pack_primary_header
        >>> from sattelemetry.channels import TelemetryChannel
        >>> from sattelemetry.crc import append_crc
        >>> layout = PacketLayout(
        ...     name="housekeeping", apid=100,
        ...     channels=(TelemetryChannel("battery_voltage", 0, "u16", "V", (0.0, 5.0 / 4095.0)),),
        ... )
        >>> data = append_crc(struct.pack(">H", 3200))
        >>> packet = pack_primary_header(apid=100, data_length=len(data)) + data
        >>> decoded = TelemetryDecoder([layout]).decode(packet)
        >>> round(decoded.values["battery_voltage"], 3)
        3.907

        """
        header = unpack_primary_header(raw_packet)
        if header.apid not in self._layouts_by_apid:
            raise InvalidPacketError(
                f"no registered packet layout for APID {header.apid}; "
                f"known APIDs: {sorted(self._layouts_by_apid)}"
            )
        layout = self._layouts_by_apid[header.apid]

        expected_total = 6 + header.data_length
        if len(raw_packet) < expected_total:
            raise InvalidPacketError(
                f"packet declares {header.data_length} data bytes (total "
                f"{expected_total} bytes) but only {len(raw_packet)} bytes were given"
            )

        data_field = raw_packet[6 : 6 + header.data_length]

        if layout.has_crc:
            data_with_crc = raw_packet[6:expected_total]
            if verify_checksum and not verify_crc(data_with_crc):
                raise ChecksumError(
                    f"CRC verification failed for packet with APID {header.apid} "
                    f"(layout {layout.name!r})"
                )
            data_field = data_with_crc[:-2]

        raw_values: dict[str, int | float] = {}
        values: dict[str, float] = {}
        for ch in layout.channels:
            end = ch.byte_offset + ch.byte_width
            if end > len(data_field):
                raise InvalidPacketError(
                    f"channel {ch.name!r} (offset {ch.byte_offset}, width {ch.byte_width}) "
                    f"extends past the packet's data field (length {len(data_field)})"
                )
            fmt_char = RAW_TYPES[ch.raw_type][0]
            (raw_value,) = struct.unpack(f">{fmt_char}", data_field[ch.byte_offset : end])
            raw_values[ch.name] = raw_value
            values[ch.name] = ch.to_engineering_units(raw_value)

        return DecodedPacket(
            header=header, layout_name=layout.name, values=values, raw_values=raw_values
        )
