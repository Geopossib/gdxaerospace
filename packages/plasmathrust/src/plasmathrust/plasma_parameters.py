"""Fundamental plasma parameters for GDX Aerospace.

Covers Debye length, plasma and cyclotron frequencies, Larmor radius,
Hall parameter, and Bohm velocity.

Reference
---------
- Chen, F.F., *Introduction to Plasma Physics and Controlled Fusion*, 3rd
  ed., Ch. 1 (Debye length, plasma frequency) and Ch. 2 (cyclotron motion,
  Larmor radius).
- Lieberman, M.A. & Lichtenberg, A.J., *Principles of Plasma Discharges
  and Materials Processing*, 2nd ed., Ch. 2 (Bohm velocity, sheath
  physics) -- the same framework used for Hall-thruster and ion-thruster
  plasma analysis (Goebel & Katz, *Fundamentals of Electric Propulsion*).

Assumptions
-----------
- All formulas assume a fully ionized, quasi-neutral, non-relativistic
  plasma with a Maxwellian electron energy distribution.
- ``electron_temperature`` parameters are given in electron-volts (eV),
  the conventional unit in plasma physics, and are converted to Joules
  internally via ``kTe = Te[eV] * e``.
- The Bohm velocity assumes ``Ti << Te``, standard for weakly-ionized
  discharge and thruster plasmas.
"""

from __future__ import annotations

import math

from plasmathrust.constants import ELECTRON_MASS, ELEMENTARY_CHARGE, VACUUM_PERMITTIVITY
from plasmathrust.exceptions import InvalidPlasmaParameterError


def debye_length(electron_density: float, electron_temperature_ev: float) -> float:
    """Debye length: ``lambda_D = sqrt(eps0 * kTe / (n_e * e^2))``.

    The characteristic distance over which a plasma screens out electric
    fields; also the sheath-thickness scale at a plasma boundary.

    Parameters
    ----------
    electron_density:
        Electron number density, m^-3, > 0.
    electron_temperature_ev:
        Electron temperature, eV, > 0.

    Returns
    -------
    float
        Debye length, m.

    Example
    -------
    >>> round(debye_length(electron_density=1e18, electron_temperature_ev=20.0) * 1e6, 2)
    33.25

    """
    if electron_density <= 0:
        raise InvalidPlasmaParameterError(
            f"electron_density must be positive, got {electron_density!r}"
        )
    if electron_temperature_ev <= 0:
        raise InvalidPlasmaParameterError(
            f"electron_temperature_ev must be positive, got {electron_temperature_ev!r}"
        )
    kte = electron_temperature_ev * ELEMENTARY_CHARGE
    return math.sqrt(VACUUM_PERMITTIVITY * kte / (electron_density * ELEMENTARY_CHARGE**2))


def plasma_frequency(electron_density: float) -> float:
    """Electron plasma frequency: ``omega_pe = sqrt(n_e * e^2 / (eps0 * m_e))``.

    Parameters
    ----------
    electron_density:
        Electron number density, m^-3, > 0.

    Returns
    -------
    float
        Angular plasma frequency, rad/s.

    Example
    -------
    >>> round(plasma_frequency(electron_density=1e18) / 1e10, 3)
    5.641

    """
    if electron_density <= 0:
        raise InvalidPlasmaParameterError(
            f"electron_density must be positive, got {electron_density!r}"
        )
    return math.sqrt(
        electron_density * ELEMENTARY_CHARGE**2 / (VACUUM_PERMITTIVITY * ELECTRON_MASS)
    )


def electron_cyclotron_frequency(magnetic_field: float) -> float:
    """Electron cyclotron (gyro) frequency: ``omega_ce = e * B / m_e``.

    Parameters
    ----------
    magnetic_field:
        Magnetic flux density, Tesla, > 0.

    Returns
    -------
    float
        Angular cyclotron frequency, rad/s.

    Example
    -------
    >>> round(electron_cyclotron_frequency(magnetic_field=0.02) / 1e9, 4)
    3.5176

    """
    if magnetic_field <= 0:
        raise InvalidPlasmaParameterError(
            f"magnetic_field must be positive, got {magnetic_field!r}"
        )
    return ELEMENTARY_CHARGE * magnetic_field / ELECTRON_MASS


def ion_cyclotron_frequency(
    magnetic_field: float, ion_mass: float, *, charge_number: int = 1
) -> float:
    """Ion cyclotron (gyro) frequency: ``omega_ci = Z * e * B / M``.

    Parameters
    ----------
    magnetic_field:
        Magnetic flux density, Tesla, > 0.
    ion_mass:
        Ion mass, kg, > 0.
    charge_number:
        Ion charge state (e.g. 1 for singly ionized), >= 1.

    Returns
    -------
    float
        Angular cyclotron frequency, rad/s.

    Example
    -------
    >>> from plasmathrust.constants import ION_MASS
    >>> round(ion_cyclotron_frequency(magnetic_field=0.02, ion_mass=ION_MASS["xenon"]), 2)
    14697.71

    """
    if magnetic_field <= 0:
        raise InvalidPlasmaParameterError(
            f"magnetic_field must be positive, got {magnetic_field!r}"
        )
    if ion_mass <= 0:
        raise InvalidPlasmaParameterError(f"ion_mass must be positive, got {ion_mass!r}")
    if charge_number < 1:
        raise InvalidPlasmaParameterError(f"charge_number must be >= 1, got {charge_number!r}")
    return charge_number * ELEMENTARY_CHARGE * magnetic_field / ion_mass


def larmor_radius(
    mass: float, perpendicular_velocity: float, magnetic_field: float, *, charge_number: int = 1
) -> float:
    """Larmor (gyro) radius: ``r_L = m * v_perp / (Z * e * B)``.

    Parameters
    ----------
    mass:
        Particle mass, kg, > 0.
    perpendicular_velocity:
        Speed component perpendicular to the magnetic field, m/s, >= 0.
    magnetic_field:
        Magnetic flux density, Tesla, > 0.
    charge_number:
        Particle charge state (magnitude), >= 1.

    Returns
    -------
    float
        Larmor radius, m.

    Example
    -------
    >>> from plasmathrust.constants import ELECTRON_MASS
    >>> round(
    ...     larmor_radius(
    ...         mass=ELECTRON_MASS, perpendicular_velocity=1e6, magnetic_field=0.02
    ...     )
    ...     * 1e6,
    ...     3,
    ... )
    284.282

    """
    if mass <= 0:
        raise InvalidPlasmaParameterError(f"mass must be positive, got {mass!r}")
    if perpendicular_velocity < 0:
        raise InvalidPlasmaParameterError(
            f"perpendicular_velocity must be non-negative, got {perpendicular_velocity!r}"
        )
    if magnetic_field <= 0:
        raise InvalidPlasmaParameterError(
            f"magnetic_field must be positive, got {magnetic_field!r}"
        )
    if charge_number < 1:
        raise InvalidPlasmaParameterError(f"charge_number must be >= 1, got {charge_number!r}")
    return mass * perpendicular_velocity / (charge_number * ELEMENTARY_CHARGE * magnetic_field)


def hall_parameter(cyclotron_frequency: float, collision_frequency: float) -> float:
    """Hall parameter: ``beta = omega_c / nu_coll`` (gyrations per collision).

    A large Hall parameter (>> 1) means the particle gyrates many times
    between collisions -- the regime exploited by Hall-effect thrusters to
    magnetize electrons while leaving the much-heavier ions unmagnetized.

    Parameters
    ----------
    cyclotron_frequency:
        Angular cyclotron frequency, rad/s, > 0.
    collision_frequency:
        Collision frequency, s^-1 (Hz), > 0.

    Returns
    -------
    float
        Hall parameter (dimensionless).

    Example
    -------
    >>> round(hall_parameter(cyclotron_frequency=1e8, collision_frequency=1e6), 1)
    100.0

    """
    if cyclotron_frequency <= 0:
        raise InvalidPlasmaParameterError(
            f"cyclotron_frequency must be positive, got {cyclotron_frequency!r}"
        )
    if collision_frequency <= 0:
        raise InvalidPlasmaParameterError(
            f"collision_frequency must be positive, got {collision_frequency!r}"
        )
    return cyclotron_frequency / collision_frequency


def bohm_velocity(electron_temperature_ev: float, ion_mass: float) -> float:
    """Bohm velocity: ``u_B = sqrt(kTe / M)``, the ion sound speed entering a sheath.

    Assumes ``Ti << Te``, standard for weakly-ionized discharge plasmas.

    Parameters
    ----------
    electron_temperature_ev:
        Electron temperature, eV, > 0.
    ion_mass:
        Ion mass, kg, > 0.

    Returns
    -------
    float
        Bohm velocity, m/s.

    Example
    -------
    >>> from plasmathrust.constants import ION_MASS
    >>> round(bohm_velocity(electron_temperature_ev=3.0, ion_mass=ION_MASS["argon"]), 1)
    2691.8

    """
    if electron_temperature_ev <= 0:
        raise InvalidPlasmaParameterError(
            f"electron_temperature_ev must be positive, got {electron_temperature_ev!r}"
        )
    if ion_mass <= 0:
        raise InvalidPlasmaParameterError(f"ion_mass must be positive, got {ion_mass!r}")
    kte = electron_temperature_ev * ELEMENTARY_CHARGE
    return math.sqrt(kte / ion_mass)
