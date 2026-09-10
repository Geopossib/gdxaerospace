"""Validate TLE parsing and checksum handling against the canonical Vallado
SGP4 verification TLE (ISS, epoch 2008)."""

from __future__ import annotations

import datetime as dt
import math

import pytest
from tletools.checksum import compute_checksum, validate_checksum
from tletools.exceptions import InvalidTLEError
from tletools.parser import epoch_to_datetime, parse_tle

_LINE1 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
_LINE2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"


def test_compute_checksum_matches_known_values() -> None:
    assert compute_checksum(_LINE1) == 7
    assert compute_checksum(_LINE2) == 7


def test_compute_checksum_rejects_short_line() -> None:
    with pytest.raises(InvalidTLEError):
        compute_checksum("1 25544U")


def test_validate_checksum_true_for_correct_lines() -> None:
    assert validate_checksum(_LINE1) is True
    assert validate_checksum(_LINE2) is True


def test_validate_checksum_false_for_corrupted_line() -> None:
    corrupted = _LINE1[:-1] + ("0" if _LINE1[-1] != "0" else "1")
    assert validate_checksum(corrupted) is False


def test_epoch_to_datetime_matches_known_date() -> None:
    """Day 264.5178... of 2008 is September 20th, per the well-known Vallado test case."""
    epoch = epoch_to_datetime(8, 264.51782528)
    assert epoch.year == 2008
    assert epoch.month == 9
    assert epoch.day == 20


def test_epoch_to_datetime_day_one_is_january_first() -> None:
    epoch = epoch_to_datetime(24, 1.0)
    assert epoch == dt.datetime(2024, 1, 1)


def test_epoch_to_datetime_year_convention_boundary() -> None:
    """Years 57-99 -> 1900s; years 0-56 -> 2000s (brackets Sputnik's 1957 launch)."""
    assert epoch_to_datetime(57, 1.0).year == 1957
    assert epoch_to_datetime(99, 1.0).year == 1999
    assert epoch_to_datetime(0, 1.0).year == 2000
    assert epoch_to_datetime(56, 1.0).year == 2056


def test_parse_tle_extracts_correct_satellite_number() -> None:
    tle = parse_tle(_LINE1, _LINE2)
    assert tle.satellite_number == 25544


def test_parse_tle_extracts_correct_orbital_elements() -> None:
    tle = parse_tle(_LINE1, _LINE2)
    assert math.isclose(tle.inclination_deg, 51.6416, rel_tol=1e-9)
    assert math.isclose(tle.raan_deg, 247.4627, rel_tol=1e-9)
    assert math.isclose(tle.eccentricity, 0.0006703, rel_tol=1e-9)
    assert math.isclose(tle.arg_perigee_deg, 130.5360, rel_tol=1e-9)
    assert math.isclose(tle.mean_anomaly_deg, 325.0288, rel_tol=1e-9)
    assert math.isclose(tle.mean_motion_rev_per_day, 15.72125391, rel_tol=1e-9)
    assert tle.revolution_number == 56353


def test_parse_tle_extracts_drag_terms() -> None:
    tle = parse_tle(_LINE1, _LINE2)
    assert math.isclose(tle.mean_motion_dot, -2.182e-05, rel_tol=1e-6)
    assert math.isclose(tle.mean_motion_ddot, 0.0, abs_tol=1e-12)
    assert math.isclose(tle.bstar, -1.1606e-05, rel_tol=1e-6)


def test_parse_tle_extracts_metadata() -> None:
    tle = parse_tle(_LINE1, _LINE2)
    assert tle.classification == "U"
    assert tle.international_designator == "98067A"
    assert tle.element_set_number == 292


def test_parse_tle_rejects_checksum_mismatch() -> None:
    corrupted = _LINE1[:-1] + ("0" if _LINE1[-1] != "0" else "1")
    with pytest.raises(InvalidTLEError):
        parse_tle(corrupted, _LINE2)


def test_parse_tle_can_skip_validation() -> None:
    corrupted = _LINE1[:-1] + ("0" if _LINE1[-1] != "0" else "1")
    tle = parse_tle(corrupted, _LINE2, validate=False)
    assert tle.satellite_number == 25544


def test_parse_tle_rejects_satellite_number_mismatch() -> None:
    bad_line2 = "2 99999  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
    bad_line2 = bad_line2[:68] + str(compute_checksum(bad_line2))
    with pytest.raises(InvalidTLEError):
        parse_tle(_LINE1, bad_line2)


def test_parse_tle_rejects_wrong_line_numbers() -> None:
    with pytest.raises(InvalidTLEError):
        parse_tle(_LINE2, _LINE1)  # swapped


def test_parse_tle_rejects_short_lines() -> None:
    with pytest.raises(InvalidTLEError):
        parse_tle("1 25544U", _LINE2)
