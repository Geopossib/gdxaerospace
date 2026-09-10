"""Validate end-to-end packet decoding: header, CRC, channel extraction, calibration."""

from __future__ import annotations

import math
import struct

import pytest
from sattelemetry.ccsds import pack_primary_header
from sattelemetry.channels import TelemetryChannel
from sattelemetry.crc import append_crc
from sattelemetry.decoder import PacketLayout, TelemetryDecoder
from sattelemetry.exceptions import ChecksumError, InvalidPacketError, UnknownChannelError


def _build_layout() -> PacketLayout:
    return PacketLayout(
        name="housekeeping",
        apid=100,
        channels=(
            TelemetryChannel("battery_voltage", 0, "u16", "V", (0.0, 5.0 / 4095.0)),
            TelemetryChannel("temperature", 2, "i16", "degC", (0.0, 0.01)),
        ),
        has_crc=True,
    )


def _build_packet(battery_raw: int, temp_raw: int, *, apid: int = 100) -> bytes:
    data_field = struct.pack(">Hh", battery_raw, temp_raw)
    data_with_crc = append_crc(data_field)
    header = pack_primary_header(apid=apid, data_length=len(data_with_crc))
    return header + data_with_crc


def test_decode_extracts_correct_calibrated_values() -> None:
    decoder = TelemetryDecoder([_build_layout()])
    packet = _build_packet(3200, -1523)
    decoded = decoder.decode(packet)
    assert math.isclose(decoded.values["battery_voltage"], 3200 * 5.0 / 4095.0, rel_tol=1e-9)
    assert math.isclose(decoded.values["temperature"], -15.23, rel_tol=1e-9)


def test_decode_extracts_correct_raw_values() -> None:
    decoder = TelemetryDecoder([_build_layout()])
    packet = _build_packet(3200, -1523)
    decoded = decoder.decode(packet)
    assert decoded.raw_values["battery_voltage"] == 3200
    assert decoded.raw_values["temperature"] == -1523


def test_decode_preserves_header_and_layout_name() -> None:
    decoder = TelemetryDecoder([_build_layout()])
    packet = _build_packet(3200, -1523)
    decoded = decoder.decode(packet)
    assert decoded.header.apid == 100
    assert decoded.layout_name == "housekeeping"


def test_decode_rejects_corrupted_checksum() -> None:
    decoder = TelemetryDecoder([_build_layout()])
    packet = _build_packet(3200, -1523)
    corrupted = packet[:-1] + bytes([packet[-1] ^ 0xFF])
    with pytest.raises(ChecksumError):
        decoder.decode(corrupted)


def test_decode_can_skip_checksum_verification() -> None:
    decoder = TelemetryDecoder([_build_layout()])
    packet = _build_packet(3200, -1523)
    corrupted = packet[:-1] + bytes([packet[-1] ^ 0xFF])
    decoded = decoder.decode(corrupted, verify_checksum=False)
    assert decoded.raw_values["battery_voltage"] == 3200


def test_decode_rejects_unknown_apid() -> None:
    decoder = TelemetryDecoder([_build_layout()])
    packet = _build_packet(3200, -1523, apid=999)
    with pytest.raises(InvalidPacketError):
        decoder.decode(packet)


def test_decode_rejects_truncated_packet() -> None:
    decoder = TelemetryDecoder([_build_layout()])
    packet = _build_packet(3200, -1523)
    with pytest.raises(InvalidPacketError):
        decoder.decode(packet[:-3])


def test_decoder_rejects_duplicate_apid_layouts() -> None:
    layout_a = PacketLayout(name="a", apid=100)
    layout_b = PacketLayout(name="b", apid=100)
    with pytest.raises(InvalidPacketError):
        TelemetryDecoder([layout_a, layout_b])


def test_layout_channel_lookup() -> None:
    layout = _build_layout()
    ch = layout.channel("battery_voltage")
    assert ch.name == "battery_voltage"


def test_layout_channel_lookup_unknown_raises() -> None:
    layout = _build_layout()
    with pytest.raises(UnknownChannelError):
        layout.channel("nonexistent")


def test_decode_without_crc_layout() -> None:
    layout = PacketLayout(
        name="no_crc",
        apid=200,
        channels=(TelemetryChannel("counter", 0, "u16"),),
        has_crc=False,
    )
    decoder = TelemetryDecoder([layout])
    data_field = struct.pack(">H", 42)
    header = pack_primary_header(apid=200, data_length=len(data_field))
    packet = header + data_field
    decoded = decoder.decode(packet)
    assert decoded.raw_values["counter"] == 42
