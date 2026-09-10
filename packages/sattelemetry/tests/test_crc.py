"""Validate CRC-16/CCITT-FALSE against the standard RevEng test vector."""

from __future__ import annotations

from sattelemetry.crc import append_crc, crc16_ccitt, verify_crc


def test_crc16_ccitt_matches_standard_check_value() -> None:
    """The standard CRC-16/CCITT-FALSE check value for '123456789' is 0x29B1."""
    assert crc16_ccitt(b"123456789") == 0x29B1


def test_crc16_ccitt_empty_input() -> None:
    """CRC of empty input is the initial value (0xFFFF), since no bytes are processed."""
    assert crc16_ccitt(b"") == 0xFFFF


def test_crc16_ccitt_deterministic() -> None:
    data = b"hello telemetry"
    assert crc16_ccitt(data) == crc16_ccitt(data)


def test_crc16_ccitt_sensitive_to_single_bit_change() -> None:
    data = b"housekeeping packet data"
    corrupted = bytearray(data)
    corrupted[0] ^= 0x01
    assert crc16_ccitt(data) != crc16_ccitt(bytes(corrupted))


def test_append_crc_appends_two_bytes() -> None:
    data = b"payload"
    result = append_crc(data)
    assert len(result) == len(data) + 2
    assert result[:-2] == data


def test_append_crc_matches_computed_crc() -> None:
    data = b"123456789"
    result = append_crc(data)
    assert int.from_bytes(result[-2:], "big") == crc16_ccitt(data)


def test_verify_crc_true_for_valid_data() -> None:
    assert verify_crc(append_crc(b"123456789")) is True


def test_verify_crc_false_for_corrupted_crc() -> None:
    assert verify_crc(b"123456789" + b"\x00\x00") is False


def test_verify_crc_false_for_corrupted_payload() -> None:
    valid = append_crc(b"123456789")
    corrupted = b"9" + valid[1:]  # corrupt first payload byte ('1' -> '9'), CRC unchanged
    assert verify_crc(corrupted) is False


def test_verify_crc_false_for_too_short_input() -> None:
    assert verify_crc(b"\x00") is False
