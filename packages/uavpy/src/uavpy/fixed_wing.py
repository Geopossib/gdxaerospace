"""Basic fixed-wing UAV sizing relations: wing loading, thrust-to-weight, stall speed.

Reference
---------
- Raymer, D.P., *Aircraft Design: A Conceptual Approach*, 6th ed., Ch. 5
  (wing loading and thrust-to-weight as the two primary conceptual-
  design sizing parameters).
- Anderson, J.D., *Aircraft Performance and Design*, Ch. 5, for the
  stall-speed relation from the lift equation at CL_max.

Assumptions
-----------
- Steady, level flight for the stall-speed relation (lift = weight).
"""

from __future__ import annotations

import math

from uavpy.exceptions import InvalidUAVInputError


def wing_loading(weight: float, wing_area: float) -> float:
    """Compute wing loading: ``W/S``.

    Parameters
    ----------
    weight:
        Aircraft weight, N, > 0.
    wing_area:
        Wing reference area, m^2, > 0.

    Returns
    -------
    float
        Wing loading, Pa (N/m^2).

    Example
    -------
    >>> round(wing_loading(weight=98.1, wing_area=0.6), 2)
    163.5

    """
    if weight <= 0:
        raise InvalidUAVInputError(f"weight must be positive, got {weight!r}")
    if wing_area <= 0:
        raise InvalidUAVInputError(f"wing_area must be positive, got {wing_area!r}")
    return weight / wing_area


def thrust_to_weight_ratio(thrust: float, weight: float) -> float:
    """Compute thrust-to-weight ratio: ``T/W``.

    Parameters
    ----------
    thrust:
        Available thrust, N, > 0.
    weight:
        Aircraft weight, N, > 0.

    Example
    -------
    >>> round(thrust_to_weight_ratio(thrust=30.0, weight=98.1), 3)
    0.306

    """
    if thrust <= 0:
        raise InvalidUAVInputError(f"thrust must be positive, got {thrust!r}")
    if weight <= 0:
        raise InvalidUAVInputError(f"weight must be positive, got {weight!r}")
    return thrust / weight


def stall_speed(
    weight: float, wing_area: float, max_lift_coefficient: float, air_density: float = 1.225
) -> float:
    """Compute stall speed from the lift equation at maximum lift coefficient.

    ``V_stall = sqrt(2*W / (rho*S*CL_max))``.

    Parameters
    ----------
    weight:
        Aircraft weight, N, > 0.
    wing_area:
        Wing reference area, m^2, > 0.
    max_lift_coefficient:
        Maximum lift coefficient, > 0.
    air_density:
        Air density, kg/m^3, > 0. Defaults to sea-level ISA.

    Returns
    -------
    float
        Stall speed, m/s.

    Example
    -------
    >>> round(stall_speed(weight=98.1, wing_area=0.6, max_lift_coefficient=1.2), 2)
    14.91

    """
    if weight <= 0:
        raise InvalidUAVInputError(f"weight must be positive, got {weight!r}")
    if wing_area <= 0:
        raise InvalidUAVInputError(f"wing_area must be positive, got {wing_area!r}")
    if max_lift_coefficient <= 0:
        raise InvalidUAVInputError(
            f"max_lift_coefficient must be positive, got {max_lift_coefficient!r}"
        )
    if air_density <= 0:
        raise InvalidUAVInputError(f"air_density must be positive, got {air_density!r}")
    return math.sqrt(2 * weight / (air_density * wing_area * max_lift_coefficient))
