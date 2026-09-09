"""Validate great-circle navigation and dead-reckoning relations."""

from __future__ import annotations

import math

import pytest
from navigationpy.exceptions import InvalidNavigationInputError
from navigationpy.great_circle import dead_reckon, great_circle_distance, initial_bearing

_JFK = (math.radians(40.6413), math.radians(-73.7781))
_LHR = (math.radians(51.4700), math.radians(-0.4543))


def test_great_circle_distance_jfk_lhr_matches_known_ballpark() -> None:
    """The JFK-LHR great circle distance is commonly cited as ~5540-5560 km."""
    distance_km = great_circle_distance(*_JFK, *_LHR) / 1000
    assert 5400 < distance_km < 5700


def test_great_circle_distance_zero_at_same_point() -> None:
    assert math.isclose(great_circle_distance(*_JFK, *_JFK), 0.0, abs_tol=1e-6)


def test_great_circle_distance_symmetric() -> None:
    d_forward = great_circle_distance(*_JFK, *_LHR)
    d_backward = great_circle_distance(*_LHR, *_JFK)
    assert math.isclose(d_forward, d_backward, rel_tol=1e-9)


def test_great_circle_distance_antipodal_is_half_circumference() -> None:
    """Antipodal points are separated by exactly half the great-circle circumference."""
    lat1, lon1 = 0.0, 0.0
    lat2, lon2 = 0.0, math.pi  # antipodal on the equator
    distance = great_circle_distance(lat1, lon1, lat2, lon2)
    circumference = 2 * math.pi * 6_371_000.0
    assert math.isclose(distance, circumference / 2, rel_tol=1e-6)


def test_great_circle_distance_rejects_invalid_latitude() -> None:
    with pytest.raises(InvalidNavigationInputError):
        great_circle_distance(math.radians(100), 0.0, 0.0, 0.0)


def test_initial_bearing_due_east_on_equator() -> None:
    """On the equator, heading to a point due east should give bearing ~90 degrees."""
    bearing = initial_bearing(0.0, 0.0, 0.0, math.radians(10))
    assert math.isclose(math.degrees(bearing), 90.0, abs_tol=1e-6)


def test_initial_bearing_due_north() -> None:
    bearing = initial_bearing(0.0, 0.0, math.radians(10), 0.0)
    assert math.isclose(math.degrees(bearing), 0.0, abs_tol=1e-6)


def test_initial_bearing_due_south() -> None:
    bearing = initial_bearing(math.radians(10), 0.0, 0.0, 0.0)
    assert math.isclose(math.degrees(bearing), 180.0, abs_tol=1e-6)


def test_initial_bearing_in_valid_range() -> None:
    bearing = initial_bearing(*_JFK, *_LHR)
    assert 0 <= bearing < 2 * math.pi


def test_initial_bearing_rejects_invalid_latitude() -> None:
    with pytest.raises(InvalidNavigationInputError):
        initial_bearing(math.radians(-100), 0.0, 0.0, 0.0)


def test_dead_reckon_zero_distance_returns_start_point() -> None:
    lat2, lon2 = dead_reckon(*_JFK, math.radians(45.0), 0.0)
    assert math.isclose(lat2, _JFK[0], abs_tol=1e-9)
    assert math.isclose(lon2, _JFK[1], abs_tol=1e-9)


def test_dead_reckon_due_north_increases_latitude_only() -> None:
    lat1, lon1 = 0.0, 0.0
    distance = 100_000.0  # 100 km
    lat2, lon2 = dead_reckon(lat1, lon1, bearing=0.0, distance=distance)
    assert lat2 > lat1
    assert math.isclose(lon2, lon1, abs_tol=1e-9)


def test_dead_reckon_round_trip_consistent_with_great_circle_distance() -> None:
    """Dead-reckoning along the initial bearing for the great-circle distance should
    land (approximately) at the destination point."""
    distance = great_circle_distance(*_JFK, *_LHR)
    bearing = initial_bearing(*_JFK, *_LHR)
    lat2, lon2 = dead_reckon(*_JFK, bearing, distance)
    assert math.isclose(lat2, _LHR[0], abs_tol=1e-3)
    assert math.isclose(lon2, _LHR[1], abs_tol=1e-3)


def test_dead_reckon_rejects_negative_distance() -> None:
    with pytest.raises(InvalidNavigationInputError):
        dead_reckon(*_JFK, math.radians(45.0), -1.0)


def test_dead_reckon_rejects_invalid_latitude() -> None:
    with pytest.raises(InvalidNavigationInputError):
        dead_reckon(math.radians(200), 0.0, 0.0, 1000.0)
