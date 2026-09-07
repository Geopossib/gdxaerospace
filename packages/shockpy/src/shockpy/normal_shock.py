"""Normal shock relations for a calorically perfect gas.

Reference
---------
- Anderson, J.D., *Fundamentals of Aerodynamics*, 6th ed., Ch. 8,
  Eqs. 8.65 (M2), 8.66 (p2/p1), 8.67 (rho2/rho1), 8.68 (T2/T1), 8.80 (p02/p01).
  Values checked against Appendix B (Normal Shock Properties table).

Assumptions
-----------
- Calorically perfect gas, adiabatic, steady 1D flow across an
  infinitesimally thin shock (Rankine-Hugoniot relations).
- Only defined for M1 > 1 (supersonic upstream flow); the second law of
  thermodynamics forbids an expansion shock (M1 < 1 -> M2 > 1) in this
  regime, so M1 <= 1 raises an error rather than returning a nonphysical
  result.
"""

from __future__ import annotations

from dataclasses import dataclass

from aerocalc.exceptions import InvalidMachNumberError
from compressibleflow.isentropic import GAMMA_AIR


@dataclass(frozen=True)
class NormalShockResult:
    """Property ratios (downstream/upstream) across a normal shock."""

    mach_upstream: float
    mach_downstream: float
    pressure_ratio: float
    temperature_ratio: float
    density_ratio: float
    stagnation_pressure_ratio: float


def normal_shock(mach1: float, *, gamma: float = GAMMA_AIR) -> NormalShockResult:
    """Compute property ratios across a normal shock, given the upstream Mach number.

    Parameters
    ----------
    mach1:
        Upstream (pre-shock) Mach number. Must be > 1.
    gamma:
        Ratio of specific heats. Defaults to 1.4 (air).

    Returns
    -------
    NormalShockResult

    Raises
    ------
    InvalidMachNumberError
        If ``mach1 <= 1`` (normal shocks only exist for supersonic upstream flow).

    Example
    -------
    >>> shock = normal_shock(2.0)
    >>> round(shock.mach_downstream, 4)
    0.5774
    >>> round(shock.pressure_ratio, 2)
    4.5

    """
    if mach1 <= 1:
        raise InvalidMachNumberError(
            mach1,
            reason=(
                "normal shocks require supersonic upstream flow (M1 > 1); "
                "an 'expansion shock' with M1 <= 1 would violate the second "
                "law of thermodynamics"
            ),
        )

    g = gamma
    m1sq = mach1**2

    m2 = ((1 + (g - 1) / 2 * m1sq) / (g * m1sq - (g - 1) / 2)) ** 0.5
    p_ratio = 1 + (2 * g / (g + 1)) * (m1sq - 1)
    rho_ratio = ((g + 1) * m1sq) / ((g - 1) * m1sq + 2)
    t_ratio = p_ratio / rho_ratio

    # Stagnation pressure ratio (Anderson Eq. 8.80).
    p0_ratio = (
        ((g + 1) * m1sq / ((g - 1) * m1sq + 2)) ** (g / (g - 1))
        * ((g + 1) / (2 * g * m1sq - (g - 1))) ** (1 / (g - 1))
    )

    return NormalShockResult(
        mach_upstream=mach1,
        mach_downstream=m2,
        pressure_ratio=p_ratio,
        temperature_ratio=t_ratio,
        density_ratio=rho_ratio,
        stagnation_pressure_ratio=p0_ratio,
    )
