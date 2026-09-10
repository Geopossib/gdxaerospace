"""TLE propagation, ground track, mission analysis, and a Walker constellation demo.

Run with:
    uv run python examples/06_orbital_mechanics_and_missions.py
"""

from __future__ import annotations

import datetime as dt
import math

from constellationpy import coverage_half_angle, walker_constellation
from groundtrack import ecef_to_geodetic, eci_to_ecef, gmst, look_angles
from missionpy import DeltaVBudget, eclipse_duration, eclipse_fraction
from orbitpy import EARTH_RADIUS, hohmann_transfer, orbital_period
from satprop import propagate_tle
from tletools import parse_tle

# The canonical Vallado/ISS validation TLE (see tletools/satprop docstrings for why
# this specific TLE is used across nearly every independent SGP4 implementation).
_LINE1 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
_LINE2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
_EPOCH = dt.datetime(2008, 9, 20, 12, 25, 40)


def tle_and_ground_track_demo() -> None:
    """Parse a TLE, propagate it, and find the sub-satellite ground point."""
    print("=== TLE parsing and ground track ===")
    tle = parse_tle(_LINE1, _LINE2)
    print(f"Satellite {tle.satellite_number} ({tle.international_designator})")
    print(f"Inclination: {tle.inclination_deg:.4f} deg, eccentricity: {tle.eccentricity:.6f}")

    position, velocity = propagate_tle(_LINE1, _LINE2, _EPOCH)
    theta = gmst(_EPOCH)
    position_ecef = eci_to_ecef(position, theta)
    lat, lon, alt = ecef_to_geodetic(position_ecef)
    print(
        f"Sub-satellite point: {math.degrees(lat):.2f} deg lat, "
        f"{math.degrees(lon):.2f} deg lon, {alt / 1000:.1f} km altitude"
    )

    # Look angles from a ground station in London.
    london_lat, london_lon = math.radians(51.5074), math.radians(-0.1278)
    az, el, rng = look_angles(london_lat, london_lon, 0.0, position_ecef)
    print(
        f"From London: azimuth {math.degrees(az):.1f} deg, "
        f"elevation {math.degrees(el):.1f} deg, range {rng / 1000:.0f} km"
    )


def mission_analysis_demo() -> None:
    """Eclipse duration and a delta-v budget for a small LEO-to-GEO mission."""
    print("\n=== Mission analysis ===")
    leo_radius = EARTH_RADIUS + 400_000.0
    period = orbital_period(leo_radius)
    fraction = eclipse_fraction(leo_radius)
    duration = eclipse_duration(leo_radius, period)
    print(
        f"400 km LEO: orbital period {period / 60:.1f} min, "
        f"eclipse fraction {fraction:.1%} ({duration / 60:.1f} min/orbit)"
    )

    geo_radius = EARTH_RADIUS + 35_786_000.0
    transfer = hohmann_transfer(leo_radius, geo_radius)
    budget = DeltaVBudget(margin_fraction=0.05)
    budget.add("LEO departure burn", transfer.delta_v1)
    budget.add("GEO insertion burn", transfer.delta_v2)
    budget.add("stationkeeping (10 yr)", 500.0)
    print(
        f"LEO->GEO Hohmann transfer: {transfer.total_delta_v:.1f} m/s over "
        f"{transfer.transfer_time / 3600:.2f} hours"
    )
    print(f"Total mission delta-v budget (5% margin): {budget.total_with_margin():.1f} m/s")


def constellation_demo() -> None:
    """Generate a small Walker constellation and check its single-satellite coverage."""
    print("\n=== Constellation geometry ===")
    slots = walker_constellation(
        total_satellites=24, num_planes=6, phase_factor=1, inclination=math.radians(55.0)
    )
    print(f"Generated {len(slots)} satellite slots across 6 planes")

    altitude = 20_200_000.0  # GPS-like altitude
    half_angle = coverage_half_angle(altitude, min_elevation=math.radians(5.0))
    print(
        f"At {altitude / 1000:.0f} km altitude with 5 deg min elevation, "
        f"each satellite covers a {math.degrees(half_angle):.1f} deg Earth central angle"
    )


if __name__ == "__main__":
    tle_and_ground_track_demo()
    mission_analysis_demo()
    constellation_demo()
