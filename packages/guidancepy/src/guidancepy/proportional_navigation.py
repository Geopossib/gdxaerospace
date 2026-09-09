"""Proportional navigation (PN) guidance law.

Reference
---------
- Zarchan, P., *Tactical and Strategic Missile Guidance*, 6th ed., AIAA,
  Ch. 2 (Eq. 2.1: line-of-sight rate; Eq. 2.4: PN acceleration command).
  Zarchan's text is the standard aerospace reference for these relations.

Assumptions
-----------
- Planar (2D) engagement geometry. A full 3D PN implementation decomposes
  into two orthogonal planes; this module handles one plane at a time.
- ``navigation_constant`` (commonly called "N") is typically in the range
  3-5 for effective intercept guidance (Zarchan Ch. 2); the module does
  not enforce this range since some studies deliberately explore outside
  it, but values well outside 2-6 usually indicate a modeling error.
"""

from __future__ import annotations

import numpy as np

from guidancepy.exceptions import InvalidGuidanceInputError


def line_of_sight_rate(relative_position: np.ndarray, relative_velocity: np.ndarray) -> float:
    """Line-of-sight rotation rate (2D): ``lambda_dot = (Px*Vy - Py*Vx) / R^2``.

    Parameters
    ----------
    relative_position:
        Target-minus-interceptor position, ``[Px, Py]``, m, shape ``(2,)``.
        Must not be the zero vector (coincident positions).
    relative_velocity:
        Target-minus-interceptor velocity, ``[Vx, Vy]``, m/s, shape ``(2,)``.

    Returns
    -------
    float
        Line-of-sight rotation rate, rad/s.

    Example
    -------
    >>> import numpy as np
    >>> round(line_of_sight_rate(np.array([1000.0, 0.0]), np.array([-200.0, 50.0])), 5)
    0.05

    """
    p = np.asarray(relative_position, dtype=float)
    v = np.asarray(relative_velocity, dtype=float)
    if p.shape != (2,) or v.shape != (2,):
        raise InvalidGuidanceInputError(
            "relative_position and relative_velocity must each have shape (2,)"
        )
    range_sq = float(p @ p)
    if range_sq < 1e-12:
        raise InvalidGuidanceInputError(
            "relative_position must not be (near) zero -- interceptor and target coincide"
        )
    return float((p[0] * v[1] - p[1] * v[0]) / range_sq)


def closing_velocity(relative_position: np.ndarray, relative_velocity: np.ndarray) -> float:
    """Compute closing velocity: ``Vc = -dR/dt = -(P . V) / |P|``.

    Positive when the range is decreasing (interceptor and target closing).

    Parameters
    ----------
    relative_position:
        Target-minus-interceptor position, ``[Px, Py]``, m, shape ``(2,)``.
        Must not be the zero vector.
    relative_velocity:
        Target-minus-interceptor velocity, ``[Vx, Vy]``, m/s, shape ``(2,)``.

    Returns
    -------
    float
        Closing velocity, m/s (positive = closing, negative = opening).

    Example
    -------
    >>> import numpy as np
    >>> round(closing_velocity(np.array([1000.0, 0.0]), np.array([-200.0, 50.0])), 2)
    200.0

    """
    p = np.asarray(relative_position, dtype=float)
    v = np.asarray(relative_velocity, dtype=float)
    if p.shape != (2,) or v.shape != (2,):
        raise InvalidGuidanceInputError(
            "relative_position and relative_velocity must each have shape (2,)"
        )
    r = float(np.linalg.norm(p))
    if r < 1e-6:
        raise InvalidGuidanceInputError(
            "relative_position must not be (near) zero -- interceptor and target coincide"
        )
    return -float(p @ v) / r


def proportional_navigation_command(
    closing_velocity_: float, los_rate: float, *, navigation_constant: float = 3.0
) -> float:
    """Proportional navigation lateral acceleration command: ``a_cmd = N * Vc * lambda_dot``.

    Commands an acceleration perpendicular to the line of sight,
    proportional to the closing velocity and the LOS rotation rate --
    the classic PN guidance law used in most tactical missile systems.

    Parameters
    ----------
    closing_velocity_:
        Closing velocity, m/s (see :func:`closing_velocity`).
    los_rate:
        Line-of-sight rotation rate, rad/s (see :func:`line_of_sight_rate`).
    navigation_constant:
        Navigation gain "N", typically 3-5.

    Returns
    -------
    float
        Commanded lateral acceleration, m/s^2.

    Example
    -------
    >>> round(proportional_navigation_command(200.0, 0.05, navigation_constant=4.0), 1)
    40.0

    """
    return navigation_constant * closing_velocity_ * los_rate


def zero_effort_miss_time_to_go(range_: float, closing_velocity_: float) -> float:
    """Estimate time-to-go: ``t_go = R / Vc``.

    Parameters
    ----------
    range_:
        Current range to target, m, > 0.
    closing_velocity_:
        Closing velocity, m/s, > 0 (must be closing, not opening).

    Returns
    -------
    float
        Estimated time to intercept, s.

    Example
    -------
    >>> round(zero_effort_miss_time_to_go(1000.0, 200.0), 2)
    5.0

    """
    if range_ <= 0:
        raise InvalidGuidanceInputError(f"range_ must be positive, got {range_!r}")
    if closing_velocity_ <= 0:
        raise InvalidGuidanceInputError(
            f"closing_velocity_ must be positive (closing), got {closing_velocity_!r}"
        )
    return range_ / closing_velocity_
