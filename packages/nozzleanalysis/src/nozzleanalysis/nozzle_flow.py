"""Isentropic converging-diverging nozzle flow analysis.

Reference
---------
- Anderson, J.D., *Fundamentals of Aerodynamics*, 6th ed., Ch. 8-10
  (choked mass flow, Eq. 10.13; area-Mach relation, Eq. 8.62).
- Sutton, G.P. & Biblarz, O., *Rocket Propulsion Elements*, 9th ed.,
  Ch. 3, for the rocket-nozzle framing of these same relations.

Assumptions
-----------
- Calorically perfect gas, isentropic, quasi-1D flow (properties uniform
  across each cross-section).
- The nozzle is choked (Mach 1 at the throat) whenever the
  back-pressure ratio permits, which is assumed throughout this module —
  it does not model the unchoked (purely subsonic venturi) regime.
"""

from __future__ import annotations

import math

from compressibleflow.isentropic import GAMMA_AIR, area_mach_ratio, stagnation_temperature_ratio

from nozzleanalysis.exceptions import InvalidNozzleInputError


def choked_mass_flow(
    chamber_pressure: float,
    chamber_temperature: float,
    throat_area: float,
    *,
    gamma: float = GAMMA_AIR,
    specific_gas_constant: float = 287.05287,
) -> float:
    """Mass flow rate through a choked (Mach-1-at-throat) nozzle.

    ``mdot = At * pc * sqrt(gamma/(R*Tc)) * (2/(gamma+1))^((gamma+1)/(2*(gamma-1)))``

    Parameters
    ----------
    chamber_pressure:
        Stagnation (chamber) pressure, Pa, > 0.
    chamber_temperature:
        Stagnation (chamber) temperature, K, > 0.
    throat_area:
        Nozzle throat area, m^2, > 0.
    gamma:
        Ratio of specific heats of the combustion/working gas.
    specific_gas_constant:
        Specific gas constant of the working gas, J/(kg*K). Defaults to
        dry air; rocket combustion gases typically have a different
        (usually lower) value that should be supplied explicitly.

    Returns
    -------
    float
        Mass flow rate, kg/s.

    Example
    -------
    >>> round(
    ...     choked_mass_flow(
    ...         chamber_pressure=7e6, chamber_temperature=3500.0, throat_area=0.01, gamma=1.22
    ...     ),
    ...     2,
    ... )
    45.56

    """
    if chamber_pressure <= 0:
        raise InvalidNozzleInputError(
            f"chamber_pressure must be positive, got {chamber_pressure!r}"
        )
    if chamber_temperature <= 0:
        raise InvalidNozzleInputError(
            f"chamber_temperature must be positive, got {chamber_temperature!r}"
        )
    if throat_area <= 0:
        raise InvalidNozzleInputError(f"throat_area must be positive, got {throat_area!r}")

    g, r = gamma, specific_gas_constant
    coeff = math.sqrt(g / (r * chamber_temperature)) * (2 / (g + 1)) ** ((g + 1) / (2 * (g - 1)))
    return float(throat_area * chamber_pressure * coeff)


def exit_mach_from_area_ratio(
    area_ratio: float,
    *,
    gamma: float = GAMMA_AIR,
    supersonic: bool = True,
    tolerance: float = 1e-9,
    max_iterations: int = 200,
) -> float:
    """Invert the isentropic area-Mach relation ``A/A*`` for the exit Mach number.

    Two solutions exist for any ``area_ratio > 1`` (one subsonic, one
    supersonic); a converging-diverging nozzle operating supersonically
    uses the supersonic branch.

    Parameters
    ----------
    area_ratio:
        Exit-to-throat area ratio ``Ae/At``, >= 1.
    gamma:
        Ratio of specific heats.
    supersonic:
        If True (default), return the supersonic-branch solution
        (``M > 1``). If False, return the subsonic-branch solution
        (``M < 1``).
    tolerance, max_iterations:
        Bisection convergence controls.

    Returns
    -------
    float
        Exit Mach number.

    Example
    -------
    >>> round(exit_mach_from_area_ratio(1.6875), 3)
    2.0

    """
    if area_ratio < 1:
        raise InvalidNozzleInputError(f"area_ratio must be >= 1, got {area_ratio!r}")
    if math.isclose(area_ratio, 1.0, abs_tol=1e-12):
        return 1.0

    if supersonic:
        lo, hi = 1.0, 50.0
        while area_mach_ratio(hi, gamma=gamma) < area_ratio:
            hi *= 2
    else:
        lo, hi = 1e-6, 1.0

    for _ in range(max_iterations):
        mid = (lo + hi) / 2
        value = area_mach_ratio(mid, gamma=gamma)
        # area_mach_ratio(M) is monotonically decreasing on (0,1] and increasing on [1,inf).
        if supersonic:
            if value < area_ratio:
                lo = mid
            else:
                hi = mid
        else:
            if value < area_ratio:
                hi = mid
            else:
                lo = mid
        if hi - lo < tolerance:
            break
    return (lo + hi) / 2


def nozzle_exit_conditions(
    chamber_temperature: float,
    exit_mach: float,
    *,
    gamma: float = GAMMA_AIR,
    specific_gas_constant: float = 287.05287,
) -> tuple[float, float]:
    """Compute static exit temperature and velocity for isentropic expansion from the chamber.

    Parameters
    ----------
    chamber_temperature:
        Stagnation (chamber) temperature, K, > 0.
    exit_mach:
        Exit Mach number, > 0.
    gamma:
        Ratio of specific heats.
    specific_gas_constant:
        Specific gas constant of the working gas, J/(kg*K).

    Returns
    -------
    (exit_temperature, exit_velocity):
        Static exit temperature (K) and velocity (m/s).

    Example
    -------
    >>> te, ve = nozzle_exit_conditions(chamber_temperature=3500.0, exit_mach=2.5, gamma=1.22)
    >>> round(te, 1)
    2074.1
    >>> round(ve, 1)
    2130.7

    """
    if chamber_temperature <= 0:
        raise InvalidNozzleInputError(
            f"chamber_temperature must be positive, got {chamber_temperature!r}"
        )
    if exit_mach <= 0:
        raise InvalidNozzleInputError(f"exit_mach must be positive, got {exit_mach!r}")

    exit_temperature = chamber_temperature / stagnation_temperature_ratio(exit_mach, gamma=gamma)
    exit_velocity = exit_mach * math.sqrt(gamma * specific_gas_constant * exit_temperature)
    return exit_temperature, exit_velocity
