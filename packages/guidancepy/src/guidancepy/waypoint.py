"""Waypoint and cross-track (line-of-sight) guidance in a local Cartesian frame.

Reference
---------
- Nelson, R.C., *Flight Stability and Automatic Control*, 2nd ed., Ch. 10,
  for waypoint-following and cross-track error concepts as used in
  autopilot/guidance loops.

Convention
----------
- Positions are 2D Cartesian ``[x, y]`` in a local frame (e.g. local-level
  north/east); bearing is measured as the standard mathematical angle
  from the +x axis, radians. For geodetic (lat/lon) navigation, see
  ``navigationpy`` instead.
"""

from __future__ import annotations

import math

import numpy as np

from guidancepy.exceptions import InvalidGuidanceInputError


def waypoint_bearing(current_position: np.ndarray, waypoint_position: np.ndarray) -> float:
    """Bearing from the current position to a waypoint: ``atan2(dy, dx)``.

    Parameters
    ----------
    current_position, waypoint_position:
        2D Cartesian positions, ``[x, y]``, m, shape ``(2,)``.

    Returns
    -------
    float
        Bearing, radians, measured from the +x axis (standard math
        convention, not compass bearing).

    Example
    -------
    >>> import numpy as np
    >>> import math
    >>> round(math.degrees(waypoint_bearing(np.array([0.0, 0.0]), np.array([100.0, 100.0]))), 2)
    45.0

    """
    cur = np.asarray(current_position, dtype=float)
    wp = np.asarray(waypoint_position, dtype=float)
    if cur.shape != (2,) or wp.shape != (2,):
        raise InvalidGuidanceInputError(
            "current_position and waypoint_position must each have shape (2,)"
        )
    delta = wp - cur
    if float(delta @ delta) < 1e-12:
        raise InvalidGuidanceInputError("current_position and waypoint_position coincide")
    return math.atan2(delta[1], delta[0])


def distance_to_waypoint(current_position: np.ndarray, waypoint_position: np.ndarray) -> float:
    """Straight-line distance from the current position to a waypoint.

    Parameters
    ----------
    current_position, waypoint_position:
        2D Cartesian positions, ``[x, y]``, m, shape ``(2,)``.

    Returns
    -------
    float
        Distance, m.

    Example
    -------
    >>> import numpy as np
    >>> distance_to_waypoint(np.array([0.0, 0.0]), np.array([3.0, 4.0]))
    5.0

    """
    cur = np.asarray(current_position, dtype=float)
    wp = np.asarray(waypoint_position, dtype=float)
    if cur.shape != (2,) or wp.shape != (2,):
        raise InvalidGuidanceInputError(
            "current_position and waypoint_position must each have shape (2,)"
        )
    return float(np.linalg.norm(wp - cur))


def cross_track_error(
    current_position: np.ndarray, path_start: np.ndarray, path_end: np.ndarray
) -> float:
    """Signed perpendicular distance from a straight-line path.

    Positive when ``current_position`` is to the left of the path
    direction (from ``path_start`` toward ``path_end``); negative when to
    the right.

    Parameters
    ----------
    current_position, path_start, path_end:
        2D Cartesian positions, ``[x, y]``, m, shape ``(2,)``.
        ``path_start`` and ``path_end`` must not coincide.

    Returns
    -------
    float
        Signed cross-track distance, m.

    Example
    -------
    >>> import numpy as np
    >>> cross_track_error(
    ...     np.array([50.0, 10.0]), np.array([0.0, 0.0]), np.array([100.0, 0.0])
    ... )
    10.0

    """
    cur = np.asarray(current_position, dtype=float)
    start = np.asarray(path_start, dtype=float)
    end = np.asarray(path_end, dtype=float)
    if cur.shape != (2,) or start.shape != (2,) or end.shape != (2,):
        raise InvalidGuidanceInputError(
            "current_position, path_start, and path_end must each have shape (2,)"
        )
    path_vector = end - start
    path_length = float(np.linalg.norm(path_vector))
    if path_length < 1e-9:
        raise InvalidGuidanceInputError("path_start and path_end must not coincide")
    unit_path = path_vector / path_length
    relative = cur - start
    return float(unit_path[0] * relative[1] - unit_path[1] * relative[0])
