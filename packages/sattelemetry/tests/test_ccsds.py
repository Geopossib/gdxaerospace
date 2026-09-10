"""Validate CCSDS primary header pack/unpack."""

from __future__ import annotations

import pytest
from sattelemetry.ccsds import (
    PACKET_TYPE_TC,
    PACKET_TYPE_TM,
    pack_primary_header,
    unpack_primary_header,
)
from sattelemetry.exceptions import InvalidPacketError


def test_pack_unpack_round_trip_all_fields() -> None:
    header_bytes = pack_primary_header(
        apid=1234,
        data_length=100,
        packet_type=PACKET_TYPE_TC,
        secondary_header_flag=True,
        sequence_flags=1,
        sequence_count=8191,
        version=0,
    )
    header = unpack_primary_header(header_bytes)
    assert header.apid == 1234
    assert header.data_length == 100
    assert header.packet_type == PACKET_TYPE_TC
    assert header.secondary_header_flag is True
    assert header.sequence_flags == 1
    assert header.sequence_count == 8191
    assert header.version == 0


def test_header_is_exactly_6_bytes() -> None:
    header_bytes = pack_primary_header(apid=100, data_length=10)
    assert len(header_bytes) == 6


def test_default_packet_type_is_telemetry() -> None:
    header = unpack_primary_header(pack_primary_header(apid=1, data_length=1))
    assert header.packet_type == PACKET_TYPE_TM


def test_data_length_zero_biased_encoding() -> None:
    """A data_length of 1 must round-trip correctly (on-wire value is length-1 = 0)."""
    header = unpack_primary_header(pack_primary_header(apid=1, data_length=1))
    assert header.data_length == 1


def test_data_length_max_value() -> None:
    header = unpack_primary_header(pack_primary_header(apid=1, data_length=65536))
    assert header.data_length == 65536


@pytest.mark.parametrize("bad_apid", [-1, 2048])
def test_pack_rejects_apid_out_of_range(bad_apid: int) -> None:
    with pytest.raises(InvalidPacketError):
        pack_primary_header(apid=bad_apid, data_length=10)


@pytest.mark.parametrize("bad_length", [0, 65537])
def test_pack_rejects_data_length_out_of_range(bad_length: int) -> None:
    with pytest.raises(InvalidPacketError):
        pack_primary_header(apid=1, data_length=bad_length)


def test_pack_rejects_invalid_packet_type() -> None:
    with pytest.raises(InvalidPacketError):
        pack_primary_header(apid=1, data_length=10, packet_type=2)


def test_pack_rejects_invalid_sequence_count() -> None:
    with pytest.raises(InvalidPacketError):
        pack_primary_header(apid=1, data_length=10, sequence_count=16384)


def test_unpack_rejects_short_data() -> None:
    with pytest.raises(InvalidPacketError):
        unpack_primary_header(b"\x00\x01\x02")
