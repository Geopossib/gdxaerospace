"""Validate telemetry channel definitions and calibration."""

from __future__ import annotations

import math

import pytest
from sattelemetry.channels import TelemetryChannel
from sattelemetry.exceptions import InvalidPacketError


def test_identity_calibration_by_default() -> None:
    channel = TelemetryChannel("raw_counter", byte_offset=0, raw_type="u16")
    assert math.isclose(channel.to_engineering_units(1234), 1234.0)


def test_linear_calibration_matches_formula() -> None:
    channel = TelemetryChannel(
        "battery_voltage", byte_offset=0, raw_type="u16", polynomial_coefficients=(0.5, 0.001)
    )
    raw = 2048
    expected = 0.5 + 0.001 * raw
    assert math.isclose(channel.to_engineering_units(raw), expected, rel_tol=1e-9)


def test_quadratic_calibration_matches_formula() -> None:
    channel = TelemetryChannel(
        "thermistor", byte_offset=0, raw_type="u16", polynomial_coefficients=(1.0, 2.0, 0.5)
    )
    raw = 10
    expected = 1.0 + 2.0 * raw + 0.5 * raw**2
    assert math.isclose(channel.to_engineering_units(raw), expected, rel_tol=1e-9)


def test_byte_width_matches_raw_type() -> None:
    assert TelemetryChannel("a", 0, "u8").byte_width == 1
    assert TelemetryChannel("b", 0, "u16").byte_width == 2
    assert TelemetryChannel("c", 0, "u32").byte_width == 4
    assert TelemetryChannel("d", 0, "f32").byte_width == 4


def test_rejects_negative_byte_offset() -> None:
    with pytest.raises(InvalidPacketError):
        TelemetryChannel("bad", byte_offset=-1, raw_type="u16")


def test_rejects_unknown_raw_type() -> None:
    with pytest.raises(InvalidPacketError):
        TelemetryChannel("bad", byte_offset=0, raw_type="u64")


def test_rejects_empty_polynomial_coefficients() -> None:
    with pytest.raises(InvalidPacketError):
        TelemetryChannel("bad", byte_offset=0, raw_type="u16", polynomial_coefficients=())
