"""Great-circle navigation on a spherical Earth model.

Covers great-circle distance, initial bearing, and dead-reckoning
position propagation.

Reference
---------
- Bowditch, N., *The American Practical Navigator*, NGA Pub. 9, Ch. 24
  (great-circle sailing formulas).
- Williams, E., *Aviation Formulary*, for the haversine distance/bearing
  and direct-geodesic dead-reckoning formulas in the exact form
  implemented here (these are the standard formulas used across aviation
  and marine navigation software).

Assumptions
-----------
- Earth is modeled as a sphere of mean radius 6,371,000 m (IUGG mean
  radius). This introduces up to ~0.3% error relative to the WGS84
  ellipsoid -- adequate for flight-planning-level navigation, not for
  survey-grade geodesy.
- All latitude/longitude arguments and return values are in radians.
  Convert from degrees at the call site (``math.radians``) as needed.
"""

from __future__ import annotations

import math

from navigationpy.exceptions import InvalidNavigationInputError

#: Mean Earth radius (IUGG), m.
EARTH_RADIUS = 6_371_000.0


def _check_latitude(lat: float, name: str) -> None:
    if not (-math.pi / 2 <= lat <= math.pi / 2):
        raise InvalidNavigationInputError(
            f"{name} must be in [-pi/2, pi/2] radians ([-90, 90] degrees), got {lat!r}"
        )


def great_circle_distance(
    lat1: float, lon1: float, lat2: float, lon2: float, *, radius: float = EARTH_RADIUS
) -> float:
    """Great-circle distance between two points via the haversine formula.

    Parameters
    ----------
    lat1, lon1:
        Latitude/longitude of the first point, radians.
    lat2, lon2:
        Latitude/longitude of the second point, radians.
    radius:
        Sphere radius, m. Defaults to Earth's mean radius.

    Returns
    -------
    float
        Great-circle distance, m.

    Example
    -------
    >>> import math
    >>> jfk = (math.radians(40.6413), math.radians(-73.7781))
    >>> lhr = (math.radians(51.4700), math.radians(-0.4543))
    >>> round(great_circle_distance(*jfk, *lhr) / 1000, 0)
    5540.0

    """
    _check_latitude(lat1, "lat1")
    _check_latitude(lat2, "lat2")
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def initial_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute the initial great-circle bearing from point 1 to point 2.

    Parameters
    ----------
    lat1, lon1, lat2, lon2:
        Latitude/longitude, radians.

    Returns
    -------
    float
        Initial bearing, radians, measured clockwise from true north,
        in ``[0, 2*pi)``.

    Example
    -------
    >>> import math
    >>> jfk = (math.radians(40.6413), math.radians(-73.7781))
    >>> lhr = (math.radians(51.4700), math.radians(-0.4543))
    >>> round(math.degrees(initial_bearing(*jfk, *lhr)), 1)
    51.4

    """
    _check_latitude(lat1, "lat1")
    _check_latitude(lat2, "lat2")
    dlon = lon2 - lon1
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    return math.atan2(y, x) % (2 * math.pi)


def dead_reckon(
    lat1: float, lon1: float, bearing: float, distance: float, *, radius: float = EARTH_RADIUS
) -> tuple[float, float]:
    """Compute the destination point given a start point, initial bearing, and distance.

    Solves the direct geodesic problem on a sphere: propagates along a
    great circle from the start point.

    Parameters
    ----------
    lat1, lon1:
        Starting latitude/longitude, radians.
    bearing:
        Initial bearing, radians, clockwise from true north.
    distance:
        Distance traveled, m, >= 0.
    radius:
        Sphere radius, m. Defaults to Earth's mean radius.

    Returns
    -------
    (lat2, lon2):
        Destination latitude/longitude, radians.

    Example
    -------
    >>> import math
    >>> jfk = (math.radians(40.6413), math.radians(-73.7781))
    >>> lat2, lon2 = dead_reckon(*jfk, math.radians(51.4), 5_540_000.0)
    >>> round(math.degrees(lat2), 2), round(math.degrees(lon2), 2)
    (51.44, -0.47)

    """
    _check_latitude(lat1, "lat1")
    if distance < 0:
        raise InvalidNavigationInputError(f"distance must be non-negative, got {distance!r}")
    angular_distance = distance / radius
    lat2 = math.asin(
        math.sin(lat1) * math.cos(angular_distance)
        + math.cos(lat1) * math.sin(angular_distance) * math.cos(bearing)
    )
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(angular_distance) * math.cos(lat1),
        math.cos(angular_distance) - math.sin(lat1) * math.sin(lat2),
    )
    return lat2, lon2
