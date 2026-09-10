"""Walker-pattern (Delta) constellation geometry.

Reference
---------
- Walker, J.G., "Satellite Constellations", Journal of the British
  Interplanetary Society, 1984 (the original Walker Delta pattern).
- Wertz, J.R. & Larson, W.J. (eds.), *Space Mission Analysis and
  Design* (SMAD), 3rd ed., Ch. 7, for the standard "i:t/p/f" notation
  and RAAN/mean-anomaly assignment formulas used here.

Convention
----------
- A Walker Delta pattern is specified as ``i:t/p/f``: inclination
  ``i``, total satellite count ``t``, number of orbital planes ``p``
  (evenly spaced in RAAN), and phasing factor ``f`` (0 to p-1), which
  offsets the mean anomaly pattern between adjacent planes.
- All satellites share the same altitude (semi-major axis) and
  inclination; only RAAN and mean anomaly vary between satellites.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from orbitpy.constants import EARTH_RADIUS

from constellationpy.exceptions import InvalidConstellationError


@dataclass(frozen=True)
class SatelliteSlot:
    """One satellite's orbital "slot" in a Walker constellation."""

    plane_index: int
    slot_index: int
    raan: float
    mean_anomaly: float


def walker_constellation(
    total_satellites: int, num_planes: int, phase_factor: int, inclination: float
) -> list[SatelliteSlot]:
    """Generate the RAAN/mean-anomaly pattern for a Walker Delta constellation.

    Parameters
    ----------
    total_satellites:
        Total number of satellites ``t``, > 0, must be evenly divisible
        by ``num_planes``.
    num_planes:
        Number of orbital planes ``p``, > 0.
    phase_factor:
        Walker phasing factor ``f``, an integer in ``[0, num_planes - 1]``.
    inclination:
        Common inclination for all satellites, radians. Not used in the
        RAAN/mean-anomaly pattern itself, but every real constellation
        needs a shared inclination alongside the pattern -- pass it
        through here so callers building full state vectors (e.g. via
        :func:`orbitpy.kepler_to_cartesian`) have one place to get it
        alongside each slot.

    Returns
    -------
    list[SatelliteSlot]
        One entry per satellite, in plane-major order.

    Raises
    ------
    InvalidConstellationError
        If ``total_satellites`` is not evenly divisible by
        ``num_planes``, or ``phase_factor`` is out of range.

    Example
    -------
    A small 6-satellite, 3-plane, phase-factor-1 Walker pattern:

    >>> slots = walker_constellation(
    ...     total_satellites=6, num_planes=3, phase_factor=1, inclination=0.9
    ... )
    >>> len(slots)
    6
    >>> [round(math.degrees(s.raan), 1) for s in slots[::2]]
    [0.0, 120.0, 240.0]

    """
    if total_satellites <= 0:
        raise InvalidConstellationError(
            f"total_satellites must be positive, got {total_satellites!r}"
        )
    if num_planes <= 0:
        raise InvalidConstellationError(f"num_planes must be positive, got {num_planes!r}")
    if total_satellites % num_planes != 0:
        raise InvalidConstellationError(
            f"total_satellites ({total_satellites}) must be evenly divisible "
            f"by num_planes ({num_planes})"
        )
    if not (0 <= phase_factor < num_planes):
        raise InvalidConstellationError(
            f"phase_factor must be in [0, num_planes - 1] = [0, {num_planes - 1}], "
            f"got {phase_factor!r}"
        )

    sats_per_plane = total_satellites // num_planes
    raan_spacing = 2 * math.pi / num_planes
    intra_plane_spacing = 2 * math.pi / sats_per_plane
    phase_spacing = 2 * math.pi * phase_factor / total_satellites

    slots = []
    for plane_index in range(num_planes):
        raan = plane_index * raan_spacing
        for slot_index in range(sats_per_plane):
            mean_anomaly = (
                slot_index * intra_plane_spacing + plane_index * phase_spacing
            ) % (2 * math.pi)
            slots.append(SatelliteSlot(plane_index, slot_index, raan, mean_anomaly))
    return slots


def coverage_half_angle(
    altitude: float, min_elevation: float, *, earth_radius: float = EARTH_RADIUS
) -> float:
    """Compute the Earth central angle covered by one satellite at a minimum elevation.

    Parameters
    ----------
    altitude:
        Satellite altitude above the surface, m, > 0.
    min_elevation:
        Minimum required elevation angle above the local horizon for
        coverage, radians, in ``[0, pi/2)``.
    earth_radius:
        Earth (or other body) radius, m.

    Returns
    -------
    float
        Earth central angle (half-angle of the coverage circle), radians.

    Example
    -------
    >>> round(math.degrees(coverage_half_angle(altitude=700_000.0, min_elevation=0.0)), 2)
    25.7

    """
    if altitude <= 0:
        raise InvalidConstellationError(f"altitude must be positive, got {altitude!r}")
    if not (0 <= min_elevation < math.pi / 2):
        raise InvalidConstellationError(
            f"min_elevation must be in [0, pi/2), got {min_elevation!r}"
        )
    r = earth_radius + altitude
    nadir_angle = math.asin((earth_radius / r) * math.cos(min_elevation))
    return math.pi / 2 - min_elevation - nadir_angle


def coverage_ground_range(
    altitude: float, min_elevation: float, *, earth_radius: float = EARTH_RADIUS
) -> float:
    """Compute the great-circle ground range of a single satellite's coverage circle.

    ``range = earth_radius * coverage_half_angle``.

    Parameters
    ----------
    altitude:
        Satellite altitude above the surface, m, > 0.
    min_elevation:
        Minimum elevation angle, radians, in ``[0, pi/2)``.
    earth_radius:
        Earth (or other body) radius, m.

    Returns
    -------
    float
        Ground-range radius of the coverage circle, m.

    Example
    -------
    >>> round(coverage_ground_range(altitude=700_000.0, min_elevation=0.0) / 1000, 1)
    2860.5

    """
    half_angle = coverage_half_angle(altitude, min_elevation, earth_radius=earth_radius)
    return earth_radius * half_angle
