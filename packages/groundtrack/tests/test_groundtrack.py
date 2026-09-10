"""Validate Julian date, GMST, ECI/ECEF rotation, geodetic conversions, and look angles."""

from __future__ import annotations

import datetime as dt
import math

import numpy as np
import pytest
from groundtrack.exceptions import InvalidCoordinateError
from groundtrack.geodetic import ecef_to_geodetic, geodetic_to_ecef, look_angles
from groundtrack.time_frames import ecef_to_eci, eci_to_ecef, gmst, julian_date


def test_julian_date_j2000_epoch() -> None:
    """J2000.0 is by definition JD 2451545.0."""
    assert julian_date(dt.datetime(2000, 1, 1, 12, 0, 0)) == 2451545.0


def test_julian_date_increases_by_one_per_day() -> None:
    jd1 = julian_date(dt.datetime(2024, 6, 15, 0, 0, 0))
    jd2 = julian_date(dt.datetime(2024, 6, 16, 0, 0, 0))
    assert math.isclose(jd2 - jd1, 1.0, rel_tol=1e-9)


def test_gmst_at_j2000_matches_defining_value() -> None:
    """GMST at J2000.0 is 280.46061837 degrees by definition of the formula."""
    theta = gmst(dt.datetime(2000, 1, 1, 12, 0, 0))
    assert math.isclose(math.degrees(theta), 280.46061837, rel_tol=1e-9)


def test_gmst_in_valid_range() -> None:
    for year in (2000, 2010, 2020, 2030):
        theta = gmst(dt.datetime(year, 6, 15, 12, 0, 0))
        assert 0 <= theta < 2 * math.pi


def test_gmst_advances_by_roughly_360_degrees_per_day() -> None:
    """GMST advances slightly faster than 360 deg/solar day (sidereal vs solar day);
    the excess beyond a full 360-degree wrap is about 0.9856 deg/day (~3m56s)."""
    theta1 = gmst(dt.datetime(2024, 6, 15, 0, 0, 0))
    theta2 = gmst(dt.datetime(2024, 6, 16, 0, 0, 0))
    excess_deg = math.degrees((theta2 - theta1) % (2 * math.pi))
    assert math.isclose(excess_deg, 0.9856, rel_tol=1e-2)


def test_eci_to_ecef_identity_at_zero_gmst() -> None:
    r = np.array([7_000_000.0, 1_000_000.0, 500_000.0])
    assert np.allclose(eci_to_ecef(r, 0.0), r)


def test_eci_ecef_round_trip() -> None:
    r = np.array([7_000_000.0, 1_000_000.0, 500_000.0])
    theta = math.radians(123.4)
    assert np.allclose(ecef_to_eci(eci_to_ecef(r, theta), theta), r)


def test_eci_to_ecef_preserves_magnitude() -> None:
    """Rotation must preserve vector length."""
    r = np.array([7_000_000.0, 1_000_000.0, 500_000.0])
    r_ecef = eci_to_ecef(r, math.radians(50.0))
    assert math.isclose(float(np.linalg.norm(r_ecef)), float(np.linalg.norm(r)), rel_tol=1e-9)


def test_eci_to_ecef_rejects_bad_shape() -> None:
    with pytest.raises(InvalidCoordinateError):
        eci_to_ecef(np.array([1.0, 0.0]), 0.0)


# --- Geodetic conversions ---


def test_geodetic_to_ecef_equator_zero_altitude() -> None:
    r = geodetic_to_ecef(0.0, 0.0, 0.0)
    assert math.isclose(r[0], 6_378_137.0, rel_tol=1e-9)
    assert math.isclose(r[1], 0.0, abs_tol=1e-6)
    assert math.isclose(r[2], 0.0, abs_tol=1e-6)


def test_geodetic_to_ecef_north_pole() -> None:
    r = geodetic_to_ecef(math.pi / 2, 0.0, 0.0)
    # WGS84 semi-minor axis (polar radius) is about 6,356,752.3 m.
    assert math.isclose(r[2], 6_356_752.3, rel_tol=1e-6)
    assert math.isclose(r[0], 0.0, abs_tol=1e-3)


def test_geodetic_to_ecef_rejects_invalid_latitude() -> None:
    with pytest.raises(InvalidCoordinateError):
        geodetic_to_ecef(math.radians(100), 0.0, 0.0)


@pytest.mark.parametrize(
    "lat_deg,lon_deg,alt",
    [
        (0.0, 0.0, 0.0),
        (40.0, -75.0, 0.0),
        (51.5, 0.0, 100.0),
        (-33.8, 151.2, 500.0),
        (89.9, 45.0, 1000.0),
        (-89.9, -30.0, 200.0),
    ],
)
def test_geodetic_ecef_round_trip(lat_deg: float, lon_deg: float, alt: float) -> None:
    lat, lon = math.radians(lat_deg), math.radians(lon_deg)
    ecef = geodetic_to_ecef(lat, lon, alt)
    lat2, lon2, alt2 = ecef_to_geodetic(ecef)
    assert math.isclose(lat2, lat, abs_tol=1e-9)
    assert math.isclose(lon2, lon, abs_tol=1e-9)
    assert math.isclose(alt2, alt, abs_tol=1e-3)


def test_ecef_to_geodetic_polar_axis_special_case() -> None:
    lat, lon, alt = ecef_to_geodetic(np.array([0.0, 0.0, 6_356_752.3]))
    assert math.isclose(lat, math.pi / 2, abs_tol=1e-6)
    assert math.isclose(alt, 0.0, abs_tol=1.0)


def test_ecef_to_geodetic_rejects_bad_shape() -> None:
    with pytest.raises(InvalidCoordinateError):
        ecef_to_geodetic(np.array([1.0, 0.0]))


# --- Look angles ---


def test_look_angles_zenith_target() -> None:
    lat, lon = math.radians(40.0), math.radians(-75.0)
    target = geodetic_to_ecef(lat, lon, 500_000.0)
    az, el, rng = look_angles(lat, lon, 0.0, target)
    assert math.isclose(math.degrees(el), 90.0, abs_tol=0.01)
    assert math.isclose(rng, 500_000.0, rel_tol=1e-3)


def test_look_angles_horizon_target_has_negative_elevation() -> None:
    """A target on the far side of the curved Earth should be below the local horizon."""
    lat, lon = math.radians(0.0), math.radians(0.0)
    far_target = geodetic_to_ecef(math.radians(0.0), math.radians(90.0), 0.0)
    _, el, _ = look_angles(lat, lon, 0.0, far_target)
    assert el < 0


def test_look_angles_range_matches_euclidean_distance() -> None:
    lat, lon, alt = math.radians(10.0), math.radians(20.0), 0.0
    observer_ecef = geodetic_to_ecef(lat, lon, alt)
    target = observer_ecef + np.array([10_000.0, 5_000.0, 2_000.0])
    _, _, rng = look_angles(lat, lon, alt, target)
    expected = float(np.linalg.norm(target - observer_ecef))
    assert math.isclose(rng, expected, rel_tol=1e-9)


def test_look_angles_azimuth_in_valid_range() -> None:
    lat, lon = math.radians(40.0), math.radians(-75.0)
    target = geodetic_to_ecef(lat, lon, 500_000.0) + np.array([1000.0, 2000.0, -500.0])
    az, _, _ = look_angles(lat, lon, 0.0, target)
    assert 0 <= az < 2 * math.pi


def test_look_angles_rejects_coincident_observer_and_target() -> None:
    lat, lon = math.radians(40.0), math.radians(-75.0)
    observer_ecef = geodetic_to_ecef(lat, lon, 0.0)
    with pytest.raises(InvalidCoordinateError):
        look_angles(lat, lon, 0.0, observer_ecef)
