"""Validate Walker constellation pattern generation and coverage geometry."""

from __future__ import annotations

import math

import pytest
from constellationpy.exceptions import InvalidConstellationError
from constellationpy.walker import (
    coverage_ground_range,
    coverage_half_angle,
    walker_constellation,
)


def test_walker_constellation_returns_correct_satellite_count() -> None:
    slots = walker_constellation(66, 6, 2, math.radians(86.4))
    assert len(slots) == 66


def test_walker_constellation_raans_evenly_spaced() -> None:
    slots = walker_constellation(66, 6, 2, math.radians(86.4))
    raans = sorted({round(math.degrees(s.raan), 6) for s in slots})
    assert len(raans) == 6
    diffs = [raans[i + 1] - raans[i] for i in range(len(raans) - 1)]
    assert all(math.isclose(d, 60.0, rel_tol=1e-9) for d in diffs)


def test_walker_constellation_mean_anomalies_evenly_spaced_within_plane() -> None:
    slots = walker_constellation(66, 6, 2, math.radians(86.4))
    plane0 = sorted(math.degrees(s.mean_anomaly) for s in slots if s.plane_index == 0)
    diffs = [plane0[i + 1] - plane0[i] for i in range(len(plane0) - 1)]
    expected_spacing = 360.0 / 11
    assert all(math.isclose(d, expected_spacing, rel_tol=1e-6) for d in diffs)


def test_walker_constellation_small_pattern_matches_hand_calculation() -> None:
    """6 satellites, 3 planes, phase factor 1: RAANs at 0/120/240 deg,
    plane 0 slots at 0/180 deg."""
    slots = walker_constellation(
        total_satellites=6, num_planes=3, phase_factor=1, inclination=0.9
    )
    plane0 = [s for s in slots if s.plane_index == 0]
    mean_anomalies_deg = sorted(math.degrees(s.mean_anomaly) for s in plane0)
    assert mean_anomalies_deg == pytest.approx([0.0, 180.0], abs=1e-6)


def test_walker_constellation_rejects_non_divisible_pattern() -> None:
    with pytest.raises(InvalidConstellationError):
        walker_constellation(10, 3, 0, 0.9)  # 10 not divisible by 3


def test_walker_constellation_rejects_invalid_phase_factor() -> None:
    with pytest.raises(InvalidConstellationError):
        walker_constellation(6, 3, 3, 0.9)  # phase_factor must be < num_planes
    with pytest.raises(InvalidConstellationError):
        walker_constellation(6, 3, -1, 0.9)


def test_walker_constellation_rejects_nonpositive_counts() -> None:
    with pytest.raises(InvalidConstellationError):
        walker_constellation(0, 3, 0, 0.9)
    with pytest.raises(InvalidConstellationError):
        walker_constellation(6, 0, 0, 0.9)


def test_coverage_half_angle_matches_formula() -> None:
    altitude, min_elev = 700_000.0, 0.0
    from orbitpy.constants import EARTH_RADIUS

    r = EARTH_RADIUS + altitude
    nadir_angle = math.asin((EARTH_RADIUS / r) * math.cos(min_elev))
    expected = math.pi / 2 - min_elev - nadir_angle
    assert math.isclose(coverage_half_angle(altitude, min_elev), expected, rel_tol=1e-9)


def test_coverage_half_angle_decreases_with_min_elevation() -> None:
    """Requiring a higher minimum elevation shrinks the usable coverage circle."""
    low_req = coverage_half_angle(700_000.0, 0.0)
    high_req = coverage_half_angle(700_000.0, math.radians(30))
    assert high_req < low_req


def test_coverage_half_angle_increases_with_altitude() -> None:
    """A higher satellite sees more of the Earth's surface at the same elevation limit."""
    low_alt = coverage_half_angle(500_000.0, 0.0)
    high_alt = coverage_half_angle(35_786_000.0, 0.0)  # GEO altitude
    assert high_alt > low_alt


def test_coverage_half_angle_rejects_nonpositive_altitude() -> None:
    with pytest.raises(InvalidConstellationError):
        coverage_half_angle(0, 0.0)


def test_coverage_half_angle_rejects_invalid_elevation() -> None:
    with pytest.raises(InvalidConstellationError):
        coverage_half_angle(700_000.0, -0.1)
    with pytest.raises(InvalidConstellationError):
        coverage_half_angle(700_000.0, math.pi / 2)


def test_coverage_ground_range_matches_formula() -> None:
    from orbitpy.constants import EARTH_RADIUS

    altitude, min_elev = 700_000.0, 0.0
    half_angle = coverage_half_angle(altitude, min_elev)
    expected = EARTH_RADIUS * half_angle
    assert math.isclose(coverage_ground_range(altitude, min_elev), expected, rel_tol=1e-9)


def test_coverage_ground_range_geo_covers_large_fraction_of_earth() -> None:
    """A GEO satellite's coverage circle should span a large fraction of Earth's
    circumference (GEO satellites cover roughly a third of the globe each)."""
    from orbitpy.constants import EARTH_RADIUS

    ground_range = coverage_ground_range(35_786_000.0, 0.0)
    earth_circumference = 2 * math.pi * EARTH_RADIUS
    fraction = (2 * ground_range) / earth_circumference  # diameter / circumference
    assert 0.25 < fraction < 0.5
