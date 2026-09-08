"""Rocket engine performance relations.

Reference
---------
- Sutton, G.P. & Biblarz, O., *Rocket Propulsion Elements*, 9th ed.,
  Ch. 2-3: effective exhaust velocity (Eq. 2-5), specific impulse
  (Eq. 2-6), characteristic velocity c* (Eq. 3-30), thrust coefficient CF
  (Eq. 3-29), and the ideal (Tsiolkovsky) rocket equation (Eq. 4-13).

Assumptions
-----------
- ``effective_exhaust_velocity`` folds any pressure-thrust term into a
  single equivalent velocity ``c = F / mdot`` (Sutton's definition); for a
  perfectly expanded nozzle this equals the actual exit velocity.
- The ideal rocket equation assumes no external forces (gravity/drag
  losses are excluded) and constant effective exhaust velocity.
"""

from __future__ import annotations

import math

from rocketperf.exceptions import InvalidRocketInputError

#: Standard gravitational acceleration used to define specific impulse in seconds.
G0 = 9.80665


def effective_exhaust_velocity(thrust: float, mdot_propellant: float) -> float:
    """Effective exhaust velocity: ``c = F / mdot`` (Sutton Eq. 2-5).

    Parameters
    ----------
    thrust:
        Thrust, Newtons, > 0.
    mdot_propellant:
        Total propellant mass flow rate, kg/s, > 0.

    Example
    -------
    >>> round(effective_exhaust_velocity(thrust=100_000.0, mdot_propellant=40.0), 1)
    2500.0

    """
    if thrust <= 0:
        raise InvalidRocketInputError(f"thrust must be positive, got {thrust!r}")
    if mdot_propellant <= 0:
        raise InvalidRocketInputError(
            f"mdot_propellant must be positive, got {mdot_propellant!r}"
        )
    return thrust / mdot_propellant


def specific_impulse_rocket(effective_exhaust_velocity_: float, *, g0: float = G0) -> float:
    """Specific impulse in seconds: ``Isp = c / g0`` (Sutton Eq. 2-6).

    Parameters
    ----------
    effective_exhaust_velocity_:
        Effective exhaust velocity, m/s, > 0. See
        :func:`effective_exhaust_velocity`.
    g0:
        Standard gravitational acceleration, m/s^2.

    Example
    -------
    >>> round(specific_impulse_rocket(2500.0), 2)
    254.93

    """
    if effective_exhaust_velocity_ <= 0:
        raise InvalidRocketInputError(
            f"effective_exhaust_velocity_ must be positive, got {effective_exhaust_velocity_!r}"
        )
    return effective_exhaust_velocity_ / g0


def characteristic_velocity(chamber_pressure: float, throat_area: float, mdot: float) -> float:
    """Characteristic velocity: ``c* = pc * At / mdot`` (Sutton Eq. 3-30).

    A combustion-performance figure of merit independent of nozzle
    expansion, used to characterize propellant/chamber performance alone.

    Parameters
    ----------
    chamber_pressure:
        Chamber (stagnation) pressure, Pa, > 0.
    throat_area:
        Nozzle throat area, m^2, > 0.
    mdot:
        Total propellant mass flow rate, kg/s, > 0.

    Example
    -------
    >>> round(characteristic_velocity(chamber_pressure=7e6, throat_area=0.01, mdot=40.0), 1)
    1750.0

    """
    if chamber_pressure <= 0:
        raise InvalidRocketInputError(
            f"chamber_pressure must be positive, got {chamber_pressure!r}"
        )
    if throat_area <= 0:
        raise InvalidRocketInputError(f"throat_area must be positive, got {throat_area!r}")
    if mdot <= 0:
        raise InvalidRocketInputError(f"mdot must be positive, got {mdot!r}")
    return chamber_pressure * throat_area / mdot


def thrust_coefficient(thrust: float, chamber_pressure: float, throat_area: float) -> float:
    """Thrust coefficient: ``CF = F / (pc * At)`` (Sutton Eq. 3-29).

    Captures the amplification of thrust due to nozzle expansion, for a
    fixed chamber pressure and throat area; typically 1.4-2.0 for
    well-designed nozzles.

    Parameters
    ----------
    thrust:
        Thrust, Newtons, > 0.
    chamber_pressure:
        Chamber pressure, Pa, > 0.
    throat_area:
        Nozzle throat area, m^2, > 0.

    Example
    -------
    >>> round(thrust_coefficient(thrust=100_000.0, chamber_pressure=7e6, throat_area=0.01), 3)
    1.429

    """
    if thrust <= 0:
        raise InvalidRocketInputError(f"thrust must be positive, got {thrust!r}")
    if chamber_pressure <= 0:
        raise InvalidRocketInputError(
            f"chamber_pressure must be positive, got {chamber_pressure!r}"
        )
    if throat_area <= 0:
        raise InvalidRocketInputError(f"throat_area must be positive, got {throat_area!r}")
    return thrust / (chamber_pressure * throat_area)


def ideal_delta_v(
    effective_exhaust_velocity_: float, mass_initial: float, mass_final: float
) -> float:
    """Ideal (Tsiolkovsky) rocket equation: ``dv = c * ln(m0 / mf)`` (Sutton Eq. 4-13).

    Parameters
    ----------
    effective_exhaust_velocity_:
        Effective exhaust velocity, m/s, > 0.
    mass_initial:
        Initial (wet) vehicle mass, kg, > 0.
    mass_final:
        Final (dry, post-burn) vehicle mass, kg, ``0 < mass_final < mass_initial``.

    Returns
    -------
    float
        Ideal velocity change, m/s (no gravity or drag losses).

    Example
    -------
    >>> round(
    ...     ideal_delta_v(
    ...         effective_exhaust_velocity_=2500.0, mass_initial=1000.0, mass_final=400.0
    ...     ),
    ...     1,
    ... )
    2290.7

    """
    if effective_exhaust_velocity_ <= 0:
        raise InvalidRocketInputError(
            f"effective_exhaust_velocity_ must be positive, got {effective_exhaust_velocity_!r}"
        )
    if mass_final <= 0 or mass_initial <= 0:
        raise InvalidRocketInputError("mass_initial and mass_final must both be positive")
    if mass_final >= mass_initial:
        raise InvalidRocketInputError(
            f"mass_final ({mass_final!r}) must be less than mass_initial ({mass_initial!r})"
        )
    return effective_exhaust_velocity_ * math.log(mass_initial / mass_final)


def mass_ratio_for_delta_v(delta_v: float, effective_exhaust_velocity_: float) -> float:
    """Invert the rocket equation for the required mass ratio ``m0/mf``.

    ``m0/mf = exp(dv / c)``.

    Parameters
    ----------
    delta_v:
        Required ideal velocity change, m/s, > 0.
    effective_exhaust_velocity_:
        Effective exhaust velocity, m/s, > 0.

    Example
    -------
    >>> round(mass_ratio_for_delta_v(delta_v=2290.7, effective_exhaust_velocity_=2500.0), 3)
    2.5

    """
    if delta_v <= 0:
        raise InvalidRocketInputError(f"delta_v must be positive, got {delta_v!r}")
    if effective_exhaust_velocity_ <= 0:
        raise InvalidRocketInputError(
            f"effective_exhaust_velocity_ must be positive, got {effective_exhaust_velocity_!r}"
        )
    return math.exp(delta_v / effective_exhaust_velocity_)
