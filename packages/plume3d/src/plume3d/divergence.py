"""Simplified single-angle plume-divergence loss model.

Reference
---------
- Goebel, D.M. & Katz, I., *Fundamentals of Electric Propulsion: Ion and
  Hall Thrusters*, JPL Space Science and Technology Series, 2008, Ch. 2 --
  discusses how beam divergence reduces the axial (useful) component of
  thrust relative to the total ion kinetic power.

Assumptions
-----------
- This module uses the simplest possible divergence model: all propellant
  is assumed to leave at a single effective half-angle ``theta`` from the
  thrust axis, so only the axial component ``cos(theta)`` contributes to
  useful thrust/Isp. This is a first-order approximation.
- A more rigorous treatment integrates the actual (typically
  near-Gaussian or measured) angular current-density profile over the
  full plume solid angle, which gives a different (generally smaller)
  correction factor for the same nominal divergence half-angle. This
  module does NOT implement that integral -- treat its output as an
  optimistic (upper-bound) estimate of the divergence loss.
"""

from __future__ import annotations

import math

from plume3d.exceptions import InvalidPlumeGeometryError


def divergence_thrust_correction(half_angle: float) -> float:
    """Single-angle thrust correction factor: ``lambda = cos(theta)``.

    Parameters
    ----------
    half_angle:
        Effective plume divergence half-angle, radians, in ``[0, pi/2)``.

    Returns
    -------
    float
        Thrust correction factor, in ``(0, 1]``. Multiply the ideal
        (zero-divergence) thrust or Isp by this factor.

    Raises
    ------
    InvalidPlumeGeometryError
        If ``half_angle`` is outside ``[0, pi/2)``.

    Example
    -------
    >>> import math
    >>> round(divergence_thrust_correction(math.radians(20.0)), 4)
    0.9397

    """
    if not (0 <= half_angle < math.pi / 2):
        raise InvalidPlumeGeometryError(
            f"half_angle must be in [0, pi/2) radians, got {half_angle!r}"
        )
    return math.cos(half_angle)


def effective_thrust(ideal_thrust: float, half_angle: float) -> float:
    """Axial thrust after applying the divergence correction: ``F_eff = F_ideal * cos(theta)``.

    Parameters
    ----------
    ideal_thrust:
        Zero-divergence (fully axial) thrust, N, > 0.
    half_angle:
        Effective plume divergence half-angle, radians, in ``[0, pi/2)``.

    Example
    -------
    >>> round(effective_thrust(ideal_thrust=0.105, half_angle=0.3), 4)
    0.1003

    """
    if ideal_thrust <= 0:
        raise InvalidPlumeGeometryError(f"ideal_thrust must be positive, got {ideal_thrust!r}")
    return ideal_thrust * divergence_thrust_correction(half_angle)


def effective_specific_impulse(ideal_isp: float, half_angle: float) -> float:
    """Effective Isp after applying the divergence correction: ``Isp_eff = Isp_ideal * cos(theta)``.

    Parameters
    ----------
    ideal_isp:
        Zero-divergence specific impulse, s, > 0.
    half_angle:
        Effective plume divergence half-angle, radians, in ``[0, pi/2)``.

    Example
    -------
    >>> round(effective_specific_impulse(ideal_isp=2141.2, half_angle=0.3), 1)
    2045.6

    """
    if ideal_isp <= 0:
        raise InvalidPlumeGeometryError(f"ideal_isp must be positive, got {ideal_isp!r}")
    return ideal_isp * divergence_thrust_correction(half_angle)


def half_angle_from_correction(correction: float) -> float:
    """Invert the divergence correction factor to recover the effective half-angle.

    Parameters
    ----------
    correction:
        Thrust correction factor, in ``(0, 1]``.

    Returns
    -------
    float
        Effective divergence half-angle, radians.

    Example
    -------
    >>> import math
    >>> round(math.degrees(half_angle_from_correction(0.9397)), 1)
    20.0

    """
    if not (0 < correction <= 1):
        raise InvalidPlumeGeometryError(f"correction must be in (0, 1], got {correction!r}")
    return math.acos(correction)
