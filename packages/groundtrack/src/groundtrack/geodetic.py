"""WGS84 geodetic/ECEF conversions and topocentric look angles.

Reference
---------
- Vallado, D.A., *Fundamentals of Astrodynamics and Applications*, 4th
  ed., Ch. 3 (Algorithm 12, ECEF-to-geodetic via iteration; Algorithm
  51, topocentric look angles).
- NIMA TR8350.2, *Department of Defense World Geodetic System 1984*,
  for the WGS84 ellipsoid parameters (reused from ``orbitpy.constants``).

Assumptions
-----------
- WGS84 reference ellipsoid, no local geoid undulation correction
  (geodetic altitude here is height above the WGS84 ellipsoid, not
  above mean sea level -- the two differ by up to about 100 m
  depending on location).
- ``ecef_to_geodetic`` uses simple fixed-point iteration (Vallado's
  method); it converges quickly (a handful of iterations) for all
  points except very near Earth's center, which is not a physically
  meaningful input anyway.
"""

from __future__ import annotations

import math

import numpy as np
from orbitpy.constants import EARTH_FLATTENING, EARTH_RADIUS

from groundtrack.exceptions import InvalidCoordinateError

_E_SQUARED = 2 * EARTH_FLATTENING - EARTH_FLATTENING**2


def geodetic_to_ecef(latitude: float, longitude: float, altitude: float) -> np.ndarray:
    """Convert WGS84 geodetic coordinates to ECEF Cartesian coordinates.

    Parameters
    ----------
    latitude:
        Geodetic latitude, radians, in ``[-pi/2, pi/2]``.
    longitude:
        Longitude, radians.
    altitude:
        Height above the WGS84 ellipsoid, m.

    Returns
    -------
    numpy.ndarray
        ECEF position, m, shape ``(3,)``.

    Example
    -------
    A point on the equator at zero longitude and zero altitude should
    land exactly on the WGS84 equatorial radius:

    >>> import numpy as np
    >>> r = geodetic_to_ecef(0.0, 0.0, 0.0)
    >>> round(float(r[0]), 1)
    6378137.0

    """
    if not (-math.pi / 2 <= latitude <= math.pi / 2):
        raise InvalidCoordinateError(f"latitude must be in [-pi/2, pi/2], got {latitude!r}")

    n = EARTH_RADIUS / math.sqrt(1 - _E_SQUARED * math.sin(latitude) ** 2)
    x = (n + altitude) * math.cos(latitude) * math.cos(longitude)
    y = (n + altitude) * math.cos(latitude) * math.sin(longitude)
    z = (n * (1 - _E_SQUARED) + altitude) * math.sin(latitude)
    return np.array([x, y, z])


def ecef_to_geodetic(
    position_ecef: np.ndarray, *, tolerance: float = 1e-12, max_iterations: int = 20
) -> tuple[float, float, float]:
    """Convert ECEF Cartesian coordinates to WGS84 geodetic coordinates.

    Parameters
    ----------
    position_ecef:
        ECEF position, m, shape ``(3,)``.
    tolerance, max_iterations:
        Fixed-point iteration convergence controls.

    Returns
    -------
    (latitude, longitude, altitude):
        Geodetic latitude (rad), longitude (rad), altitude above the
        WGS84 ellipsoid (m).

    Example
    -------
    >>> import numpy as np
    >>> lat, lon, alt = ecef_to_geodetic(np.array([6_378_137.0, 0.0, 0.0]))
    >>> round(lat, 9), round(lon, 9), round(alt, 3)
    (0.0, 0.0, 0.0)

    """
    r = np.asarray(position_ecef, dtype=float)
    if r.shape != (3,):
        raise InvalidCoordinateError(f"position_ecef must have shape (3,), got {r.shape}")
    x, y, z = r
    p = math.hypot(x, y)
    longitude = math.atan2(y, x)

    if p < 1e-6:
        # On (or very near) the polar axis: latitude is +/-90 deg by definition.
        latitude = math.copysign(math.pi / 2, z) if z != 0 else 0.0
        altitude = abs(z) - EARTH_RADIUS * math.sqrt(1 - _E_SQUARED)
        return latitude, longitude, altitude

    latitude = math.atan2(z, p)
    for _ in range(max_iterations):
        n = EARTH_RADIUS / math.sqrt(1 - _E_SQUARED * math.sin(latitude) ** 2)
        new_latitude = math.atan2(z + n * _E_SQUARED * math.sin(latitude), p)
        if abs(new_latitude - latitude) < tolerance:
            latitude = new_latitude
            break
        latitude = new_latitude

    n = EARTH_RADIUS / math.sqrt(1 - _E_SQUARED * math.sin(latitude) ** 2)
    altitude = p / math.cos(latitude) - n
    return latitude, longitude, altitude


def look_angles(
    observer_lat: float,
    observer_lon: float,
    observer_alt: float,
    target_ecef: np.ndarray,
) -> tuple[float, float, float]:
    """Compute topocentric azimuth, elevation, and range from an observer to a target.

    Parameters
    ----------
    observer_lat, observer_lon, observer_alt:
        Observer's WGS84 geodetic position (rad, rad, m).
    target_ecef:
        Target ECEF position, m, shape ``(3,)``.

    Returns
    -------
    (azimuth, elevation, range):
        Azimuth (rad, clockwise from north), elevation (rad, above the
        local horizon), and slant range (m).

    Example
    -------
    A target directly above the observer (same lat/lon, higher altitude)
    should appear at zenith (elevation = 90 deg):

    >>> import math
    >>> observer_ecef = geodetic_to_ecef(math.radians(40.0), math.radians(-75.0), 0.0)
    >>> target = geodetic_to_ecef(math.radians(40.0), math.radians(-75.0), 500_000.0)
    >>> az, el, rng = look_angles(math.radians(40.0), math.radians(-75.0), 0.0, target)
    >>> round(math.degrees(el), 1)
    90.0

    """
    observer_ecef = geodetic_to_ecef(observer_lat, observer_lon, observer_alt)
    target = np.asarray(target_ecef, dtype=float)
    if target.shape != (3,):
        raise InvalidCoordinateError(f"target_ecef must have shape (3,), got {target.shape}")

    range_vector = target - observer_ecef
    rng = float(np.linalg.norm(range_vector))
    if rng < 1e-6:
        raise InvalidCoordinateError("observer and target coincide; look angles are undefined")

    sin_lat, cos_lat = math.sin(observer_lat), math.cos(observer_lat)
    sin_lon, cos_lon = math.sin(observer_lon), math.cos(observer_lon)

    # ECEF-to-local-ENU (East, North, Up) rotation.
    east = -sin_lon * range_vector[0] + cos_lon * range_vector[1]
    north = (
        -sin_lat * cos_lon * range_vector[0]
        - sin_lat * sin_lon * range_vector[1]
        + cos_lat * range_vector[2]
    )
    up = (
        cos_lat * cos_lon * range_vector[0]
        + cos_lat * sin_lon * range_vector[1]
        + sin_lat * range_vector[2]
    )

    elevation = math.asin(max(-1.0, min(1.0, up / rng)))
    azimuth = math.atan2(east, north) % (2 * math.pi)
    return azimuth, elevation, rng
