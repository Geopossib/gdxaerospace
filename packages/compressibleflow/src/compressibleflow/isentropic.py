"""Isentropic compressible-flow relations for a calorically perfect gas.

Reference
---------
- Anderson, J.D., *Fundamentals of Aerodynamics*, 6th ed., Ch. 8,
  Eqs. 8.40-8.42. Tabulated values checked against Anderson's Appendix A
  (Isentropic Flow Properties table).

Assumptions
-----------
- Calorically perfect gas (constant gamma, no dissociation/ionization) —
  breaks down above roughly Mach 5 for real air due to vibrational
  excitation and above Mach 10-12 due to dissociation.
- Adiabatic, reversible (isentropic) flow — no shocks, no heat addition,
  no friction.
"""

from __future__ import annotations

from aerocalc.exceptions import InvalidMachNumberError

#: Default ratio of specific heats for air.
GAMMA_AIR = 1.4


def _check_mach(mach: float) -> None:
    if mach < 0:
        raise InvalidMachNumberError(mach, reason="Mach number cannot be negative")


def stagnation_temperature_ratio(mach: float, *, gamma: float = GAMMA_AIR) -> float:
    """``T0/T = 1 + (gamma-1)/2 * M^2`` (Anderson Eq. 8.40).

    Parameters
    ----------
    mach:
        Freestream/local Mach number, >= 0.
    gamma:
        Ratio of specific heats. Defaults to 1.4 (air).

    Example
    -------
    >>> round(stagnation_temperature_ratio(2.0), 3)
    1.8

    """
    _check_mach(mach)
    return 1 + (gamma - 1) / 2 * mach**2


def stagnation_pressure_ratio(mach: float, *, gamma: float = GAMMA_AIR) -> float:
    """``p0/p = (T0/T)^(gamma/(gamma-1))`` (Anderson Eq. 8.42).

    Example
    -------
    >>> round(stagnation_pressure_ratio(2.0), 3)
    7.824

    """
    _check_mach(mach)
    return float(stagnation_temperature_ratio(mach, gamma=gamma) ** (gamma / (gamma - 1)))


def stagnation_density_ratio(mach: float, *, gamma: float = GAMMA_AIR) -> float:
    """``rho0/rho = (T0/T)^(1/(gamma-1))`` (Anderson Eq. 8.41).

    Example
    -------
    >>> round(stagnation_density_ratio(2.0), 3)
    4.347

    """
    _check_mach(mach)
    return float(stagnation_temperature_ratio(mach, gamma=gamma) ** (1 / (gamma - 1)))


def area_mach_ratio(mach: float, *, gamma: float = GAMMA_AIR) -> float:
    """Isentropic area ratio ``A/A*`` for a given Mach number (Anderson Eq. 8.62).

    ``A*`` is the sonic (throat) area for which this Mach number would occur
    in an isentropic nozzle/diffuser with the same mass flow.

    Parameters
    ----------
    mach:
        Mach number, > 0 (undefined at M=0).
    gamma:
        Ratio of specific heats.

    Raises
    ------
    InvalidMachNumberError
        If ``mach`` is not strictly positive.

    Example
    -------
    >>> round(area_mach_ratio(2.0), 4)
    1.6875

    """
    if mach <= 0:
        raise InvalidMachNumberError(mach, reason="area_mach_ratio requires Mach > 0")
    term = (2 / (gamma + 1)) * stagnation_temperature_ratio(mach, gamma=gamma)
    exponent = (gamma + 1) / (2 * (gamma - 1))
    return float((1 / mach) * term**exponent)
