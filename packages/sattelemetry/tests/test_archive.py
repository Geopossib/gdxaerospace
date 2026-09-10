"""Validate the in-memory telemetry archive and statistical outlier detection."""

from __future__ import annotations

import math

import pytest
from sattelemetry.archive import TelemetryArchive
from sattelemetry.exceptions import InvalidPacketError


def test_add_and_series_round_trip() -> None:
    archive = TelemetryArchive()
    archive.add(0.0, {"battery_voltage": 3.9})
    archive.add(1.0, {"battery_voltage": 3.8})
    values = [r.value for r in archive.series("battery_voltage")]
    assert values == [3.9, 3.8]


def test_add_stores_multiple_channels_from_one_packet() -> None:
    archive = TelemetryArchive()
    archive.add(0.0, {"battery_voltage": 3.9, "temperature": 21.5})
    assert len(archive.series("battery_voltage")) == 1
    assert len(archive.series("temperature")) == 1


def test_series_preserves_timestamps() -> None:
    archive = TelemetryArchive()
    archive.add(10.0, {"a": 1.0})
    archive.add(20.0, {"a": 2.0})
    timestamps = [r.timestamp for r in archive.series("a")]
    assert timestamps == [10.0, 20.0]


def test_series_empty_for_unknown_channel() -> None:
    archive = TelemetryArchive()
    archive.add(0.0, {"a": 1.0})
    assert archive.series("nonexistent") == []


def test_channels_returns_all_channel_names() -> None:
    archive = TelemetryArchive()
    archive.add(0.0, {"a": 1.0, "b": 2.0})
    archive.add(1.0, {"c": 3.0})
    assert archive.channels() == {"a", "b", "c"}


def test_len_counts_total_records() -> None:
    archive = TelemetryArchive()
    archive.add(0.0, {"a": 1.0, "b": 2.0})
    archive.add(1.0, {"a": 1.5})
    assert len(archive) == 3


def test_detect_outliers_flags_clear_outlier() -> None:
    archive = TelemetryArchive()
    readings = [3.9, 3.91, 3.89, 3.90, 3.92, 3.88, 3.91, 3.89, 3.90, 3.92, 1.0]
    for v in readings:
        archive.add(0.0, {"battery_voltage": v})
    outliers = archive.detect_outliers("battery_voltage")
    assert [r.value for r in outliers] == [1.0]


def test_detect_outliers_no_outliers_in_uniform_data() -> None:
    archive = TelemetryArchive()
    for v in [3.9, 3.91, 3.89, 3.90, 3.92]:
        archive.add(0.0, {"battery_voltage": v})
    assert archive.detect_outliers("battery_voltage") == []


def test_detect_outliers_empty_for_fewer_than_two_records() -> None:
    archive = TelemetryArchive()
    archive.add(0.0, {"a": 5.0})
    assert archive.detect_outliers("a") == []
    empty_archive = TelemetryArchive()
    assert empty_archive.detect_outliers("a") == []


def test_detect_outliers_empty_for_zero_variance() -> None:
    """If every value is identical, stdev is 0 and nothing can be a statistical outlier."""
    archive = TelemetryArchive()
    for _ in range(5):
        archive.add(0.0, {"a": 42.0})
    assert archive.detect_outliers("a") == []


def test_detect_outliers_respects_custom_threshold() -> None:
    archive = TelemetryArchive()
    for v in [10.0, 10.1, 9.9, 10.0, 12.0]:  # 12.0 is a mild outlier
        archive.add(0.0, {"a": v})
    strict = archive.detect_outliers("a", z_threshold=1.0)
    lenient = archive.detect_outliers("a", z_threshold=5.0)
    assert len(strict) >= len(lenient)


def test_detect_outliers_rejects_nonpositive_threshold() -> None:
    archive = TelemetryArchive()
    archive.add(0.0, {"a": 1.0})
    archive.add(1.0, {"a": 2.0})
    with pytest.raises(InvalidPacketError):
        archive.detect_outliers("a", z_threshold=0)
    with pytest.raises(InvalidPacketError):
        archive.detect_outliers("a", z_threshold=-1.0)


def test_detect_outliers_preserves_original_order() -> None:
    archive = TelemetryArchive()
    values = [1.0, 100.0, 1.1, 0.9, 1.0, -100.0, 1.05]
    for v in values:
        archive.add(0.0, {"a": v})
    outliers = archive.detect_outliers("a", z_threshold=1.5)
    outlier_values = [r.value for r in outliers]
    # Order in the archive is preserved: 100.0 comes before -100.0.
    assert outlier_values.index(100.0) < outlier_values.index(-100.0)


def test_archive_independent_channels_do_not_interfere() -> None:
    archive = TelemetryArchive()
    archive.add(0.0, {"a": 1.0, "b": 1000.0})
    archive.add(1.0, {"a": 1.1, "b": 1001.0})
    a_values = [r.value for r in archive.series("a")]
    b_values = [r.value for r in archive.series("b")]
    assert math.isclose(a_values[0], 1.0)
    assert math.isclose(b_values[0], 1000.0)
