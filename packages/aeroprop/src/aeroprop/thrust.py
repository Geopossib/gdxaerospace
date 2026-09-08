"""General air-breathing propulsion performance relations.

Reference
---------
- Mattingly, J.D., *Elements of Gas Turbine Propulsion*, 2nd ed.,
  Ch. 2 (uninstalled thrust equation, Eq. 2.14; specific impulse and TSFC,
  Eqs. 2.16-2.17; propulsive/Froude efficiency, Eq. 2.20).

Assumptions
-----------
- Uninstalled (net) thrust of a generic air-breathing engine: single
  inlet, single exhaust stream, steady operation.
- The propulsive-efficiency (Froude efficiency) expression assumes the
  simplest case of equal mass flow in and out (fuel mass flow neglected
  relative to air mass flow), which is standard for a first-order estimate.
"""

from __future__ import annotations

from aeroprop.exceptions import InvalidPropulsionInputError

#: Standard gravitational acceleration used to define specific impulse in seconds.
G0 = 9.80665


def thrust_airbreathing(
    mdot_air: float,
    mdot_fuel: float,
    exit_velocity: float,
    flight_velocity: float,
    *,
    exit_pressure: float | None = None,
    ambient_pressure: float | None = None,
    exit_area: float | None = None,
) -> float:
    """Uninstalled net thrust of an air-breathing engine.

    ``F = (mdot_air + mdot_fuel) * Ve - mdot_air * V0 + (pe - pa) * Ae``

    The pressure term is included only if all three of ``exit_pressure``,
    ``ambient_pressure``, and ``exit_area`` are supplied; otherwise the
    nozzle is assumed perfectly (pressure-)matched (``pe = pa``), which is
    the common simplifying assumption for a first-order estimate.

    Parameters
    ----------
    mdot_air:
        Air mass flow rate through the engine, kg/s, > 0.
    mdot_fuel:
        Fuel mass flow rate, kg/s, >= 0.
    exit_velocity:
        Nozzle exit velocity, m/s.
    flight_velocity:
        Freestream (flight) velocity, m/s.
    exit_pressure, ambient_pressure, exit_area:
        Optional pressure-thrust term inputs.

    Returns
    -------
    float
        Net thrust, Newtons.

    Example
    -------
    >>> round(
    ...     thrust_airbreathing(
    ...         mdot_air=50.0, mdot_fuel=1.0, exit_velocity=600.0, flight_velocity=250.0
    ...     ),
    ...     1,
    ... )
    18100.0

    """
    if mdot_air <= 0:
        raise InvalidPropulsionInputError(f"mdot_air must be positive, got {mdot_air!r}")
    if mdot_fuel < 0:
        raise InvalidPropulsionInputError(f"mdot_fuel must be non-negative, got {mdot_fuel!r}")

    thrust = (mdot_air + mdot_fuel) * exit_velocity - mdot_air * flight_velocity

    if exit_pressure is not None and ambient_pressure is not None and exit_area is not None:
        thrust += (exit_pressure - ambient_pressure) * exit_area

    return thrust


def specific_impulse(thrust: float, mdot_propellant: float, *, g0: float = G0) -> float:
    """Specific impulse in seconds: ``Isp = F / (mdot * g0)``.

    Parameters
    ----------
    thrust:
        Net thrust, Newtons, > 0.
    mdot_propellant:
        Total propellant (or fuel) mass flow rate, kg/s, > 0.
    g0:
        Standard gravitational acceleration, m/s^2.

    Example
    -------
    >>> round(specific_impulse(thrust=1000.0, mdot_propellant=0.34), 1)
    299.9

    """
    if thrust <= 0:
        raise InvalidPropulsionInputError(f"thrust must be positive, got {thrust!r}")
    if mdot_propellant <= 0:
        raise InvalidPropulsionInputError(
            f"mdot_propellant must be positive, got {mdot_propellant!r}"
        )
    return thrust / (mdot_propellant * g0)


def thrust_specific_fuel_consumption(mdot_fuel: float, thrust: float) -> float:
    """Thrust-specific fuel consumption: ``TSFC = mdot_fuel / F`` (kg/(N*s)).

    Parameters
    ----------
    mdot_fuel:
        Fuel mass flow rate, kg/s, > 0.
    thrust:
        Net thrust, Newtons, > 0.

    Example
    -------
    >>> round(thrust_specific_fuel_consumption(mdot_fuel=1.0, thrust=18100.0), 8)
    5.525e-05

    """
    if mdot_fuel <= 0:
        raise InvalidPropulsionInputError(f"mdot_fuel must be positive, got {mdot_fuel!r}")
    if thrust <= 0:
        raise InvalidPropulsionInputError(f"thrust must be positive, got {thrust!r}")
    return mdot_fuel / thrust


def propulsive_efficiency(flight_velocity: float, exit_velocity: float) -> float:
    """Froude (propulsive) efficiency: ``eta_p = 2*V0 / (V0 + Ve)``.

    This is the fraction of the kinetic-energy change imparted to the
    propulsive stream that goes into useful thrust power, neglecting the
    fuel mass flow (standard first-order approximation).

    Parameters
    ----------
    flight_velocity:
        Freestream (flight) velocity, m/s, > 0.
    exit_velocity:
        Nozzle exit velocity, m/s, must exceed ``flight_velocity`` for net
        thrust to exist.

    Example
    -------
    >>> round(propulsive_efficiency(flight_velocity=250.0, exit_velocity=600.0), 4)
    0.5882

    """
    if flight_velocity <= 0:
        raise InvalidPropulsionInputError(
            f"flight_velocity must be positive, got {flight_velocity!r}"
        )
    if exit_velocity <= flight_velocity:
        raise InvalidPropulsionInputError(
            f"exit_velocity ({exit_velocity!r}) must exceed flight_velocity "
            f"({flight_velocity!r}) for net thrust to be produced"
        )
    return 2 * flight_velocity / (flight_velocity + exit_velocity)
