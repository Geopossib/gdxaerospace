"""Ideal electrostatic ion acceleration: exhaust velocity, thrust, Isp, efficiency.

Reference
---------
- Goebel, D.M. & Katz, I., *Fundamentals of Electric Propulsion: Ion and
  Hall Thrusters*, JPL Space Science and Technology Series, 2008,
  Ch. 2 (Eq. 2.4-2 ideal exhaust velocity; Eq. 2.5-9 total efficiency).

Assumptions
-----------
- Ions are singly (or ``charge_number``-fold) ionized and accelerated
  from rest through the full applied voltage with no energy loss --
  the *ideal* electrostatic-acceleration exhaust velocity. Real thrusters
  fall short of this due to beam divergence, multiply-charged ions,
  and ionization/production losses (see ``plume3d`` for a divergence
  correction).
- ``thrust_efficiency`` uses total input power ``P = V * I`` and does not
  separately account for cathode-heater or magnet-coil power, which a
  full engine efficiency budget would include.
"""

from __future__ import annotations

import math

from plasmathrust.constants import ELEMENTARY_CHARGE

from electricprop.exceptions import InvalidElectricPropulsionInputError

#: Standard gravitational acceleration used to define specific impulse in seconds.
G0 = 9.80665


def ion_exhaust_velocity(voltage: float, ion_mass: float, *, charge_number: int = 1) -> float:
    """Ideal electrostatic exhaust velocity: ``Ve = sqrt(2 * Z * e * V / M)``.

    Parameters
    ----------
    voltage:
        Net accelerating voltage, V, > 0.
    ion_mass:
        Ion mass, kg, > 0 (see ``plasmathrust.constants.ION_MASS`` for
        common propellants).
    charge_number:
        Ion charge state, >= 1.

    Returns
    -------
    float
        Ideal exhaust velocity, m/s.

    Example
    -------
    >>> from plasmathrust.constants import ION_MASS
    >>> round(ion_exhaust_velocity(voltage=300.0, ion_mass=ION_MASS["xenon"]), 1)
    20998.4

    """
    if voltage <= 0:
        raise InvalidElectricPropulsionInputError(f"voltage must be positive, got {voltage!r}")
    if ion_mass <= 0:
        raise InvalidElectricPropulsionInputError(f"ion_mass must be positive, got {ion_mass!r}")
    if charge_number < 1:
        raise InvalidElectricPropulsionInputError(
            f"charge_number must be >= 1, got {charge_number!r}"
        )
    return math.sqrt(2 * charge_number * ELEMENTARY_CHARGE * voltage / ion_mass)


def thrust_from_beam_current(
    beam_current: float, voltage: float, ion_mass: float, *, charge_number: int = 1
) -> float:
    """Ideal thrust from beam current: ``F = I_b * sqrt(2 * M * V / (Z * e))``.

    Equivalent to ``F = mdot * Ve`` under the assumption that beam current
    fully accounts for the ionized propellant flow (``mdot = I_b * M / (Z * e)``).

    Parameters
    ----------
    beam_current:
        Ion beam current, A, > 0.
    voltage:
        Net accelerating voltage, V, > 0.
    ion_mass:
        Ion mass, kg, > 0.
    charge_number:
        Ion charge state, >= 1.

    Returns
    -------
    float
        Ideal thrust, N.

    Example
    -------
    >>> from plasmathrust.constants import ION_MASS
    >>> round(
    ...     thrust_from_beam_current(beam_current=5.0, voltage=300.0, ion_mass=ION_MASS["xenon"]),
    ...     3,
    ... )
    0.143

    """
    if beam_current <= 0:
        raise InvalidElectricPropulsionInputError(
            f"beam_current must be positive, got {beam_current!r}"
        )
    if voltage <= 0:
        raise InvalidElectricPropulsionInputError(f"voltage must be positive, got {voltage!r}")
    if ion_mass <= 0:
        raise InvalidElectricPropulsionInputError(f"ion_mass must be positive, got {ion_mass!r}")
    if charge_number < 1:
        raise InvalidElectricPropulsionInputError(
            f"charge_number must be >= 1, got {charge_number!r}"
        )
    return beam_current * math.sqrt(2 * ion_mass * voltage / (charge_number * ELEMENTARY_CHARGE))


def specific_impulse_electric(exhaust_velocity: float, *, g0: float = G0) -> float:
    """Specific impulse in seconds: ``Isp = Ve / g0``.

    Parameters
    ----------
    exhaust_velocity:
        Exhaust velocity, m/s, > 0.
    g0:
        Standard gravitational acceleration, m/s^2.

    Example
    -------
    >>> round(specific_impulse_electric(20998.4), 1)
    2141.2

    """
    if exhaust_velocity <= 0:
        raise InvalidElectricPropulsionInputError(
            f"exhaust_velocity must be positive, got {exhaust_velocity!r}"
        )
    return exhaust_velocity / g0


def thrust_efficiency(thrust: float, mdot: float, power: float) -> float:
    """Total thrust efficiency: ``eta_T = F^2 / (2 * mdot * P)``.

    The ratio of jet kinetic power to total input electrical power
    (Goebel & Katz Eq. 2.5-9).

    Parameters
    ----------
    thrust:
        Thrust, N, > 0.
    mdot:
        Propellant mass flow rate, kg/s, > 0.
    power:
        Total input electrical power, W, > 0.

    Returns
    -------
    float
        Thrust efficiency, dimensionless, typically in ``(0, 1)``.

    Example
    -------
    >>> round(thrust_efficiency(thrust=0.105, mdot=5e-6, power=1500.0), 3)
    0.735

    """
    if thrust <= 0:
        raise InvalidElectricPropulsionInputError(f"thrust must be positive, got {thrust!r}")
    if mdot <= 0:
        raise InvalidElectricPropulsionInputError(f"mdot must be positive, got {mdot!r}")
    if power <= 0:
        raise InvalidElectricPropulsionInputError(f"power must be positive, got {power!r}")
    return thrust**2 / (2 * mdot * power)
