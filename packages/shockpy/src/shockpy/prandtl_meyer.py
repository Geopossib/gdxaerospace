"""Prandtl-Meyer expansion function for a calorically perfect gas.

Reference
---------
- Anderson, J.D., *Fundamentals of Aerodynamics*, 6th ed., Ch. 9,
  Eq. 9.42 (Prandtl-Meyer function), Eq. 9.43 (expansion-fan turning angle).
  Values checked against Appendix C (Prandtl-Meyer function table).

Assumptions
-----------
- Calorically perfect gas, isentropic expansion via an infinite series of
  Mach waves.
- Only defined for M >= 1.
"""

from __future__ import annotations

import math

from aerocalc.exceptions import InvalidMachNumberError
from compressibleflow.isentropic import GAMMA_AIR

from shockpy.exceptions import DetachedShockError


def prandtl_meyer_angle(mach: float, *, gamma: float = GAMMA_AIR) -> float:
    """Prandtl-Meyer function ``nu(M)``: total turning angle from M=1 to ``mach``.

    Parameters
    ----------
    mach:
        Mach number, >= 1.
    gamma:
        Ratio of specific heats.

    Returns
    -------
    float
        ``nu(M)`` in radians.

    Raises
    ------
    InvalidMachNumberError
        If ``mach < 1``.

    Example
    -------
    >>> import math
    >>> round(math.degrees(prandtl_meyer_angle(2.0)), 2)
    26.38

    """
    if mach < 1:
        raise InvalidMachNumberError(mach, reason="the Prandtl-Meyer function requires M >= 1")
    g = gamma
    k = ((g + 1) / (g - 1)) ** 0.5
    return k * math.atan(((mach**2 - 1) / k**2) ** 0.5) - math.atan((mach**2 - 1) ** 0.5)


def mach_from_prandtl_meyer_angle(
    nu: float, *, gamma: float = GAMMA_AIR, tolerance: float = 1e-10, max_iterations: int = 100
) -> float:
    """Invert the Prandtl-Meyer function: find ``M`` such that ``nu(M) = nu``.

    Solved by bisection since :func:`prandtl_meyer_angle` is monotonically
    increasing in ``M`` and has no closed-form inverse.

    Parameters
    ----------
    nu:
        Target Prandtl-Meyer angle, radians, ``0 <= nu < nu_max(gamma)``.
    gamma:
        Ratio of specific heats.
    tolerance:
        Bisection convergence tolerance on the Mach number bracket width.
    max_iterations:
        Maximum number of bisection iterations.

    Returns
    -------
    float
        Mach number.

    Example
    -------
    >>> round(mach_from_prandtl_meyer_angle(prandtl_meyer_angle(2.0)), 6)
    2.0

    """
    g = gamma
    nu_max = (math.pi / 2) * (((g + 1) / (g - 1)) ** 0.5 - 1)
    if not (0 <= nu < nu_max):
        raise ValueError(
            f"nu={nu!r} rad is outside the achievable range [0, {nu_max:.6f}) rad "
            f"for gamma={gamma}."
        )
    lo, hi = 1.0, 1000.0
    for _ in range(max_iterations):
        mid = (lo + hi) / 2
        if prandtl_meyer_angle(mid, gamma=gamma) < nu:
            lo = mid
        else:
            hi = mid
        if hi - lo < tolerance:
            break
    return (lo + hi) / 2


def expansion_fan(
    mach1: float, turn_angle: float, *, gamma: float = GAMMA_AIR
) -> tuple[float, float]:
    """Downstream Mach and stagnation-pressure ratio through a Prandtl-Meyer expansion fan.

    Parameters
    ----------
    mach1:
        Upstream Mach number, >= 1.
    turn_angle:
        Convex corner turning angle, radians, > 0.
    gamma:
        Ratio of specific heats.

    Returns
    -------
    (mach2, stagnation_pressure_ratio):
        Downstream Mach number and ``p02/p01``. Expansions are isentropic,
        so ``p02/p01 = 1.0`` always.

    Example
    -------
    >>> m2, p0_ratio = expansion_fan(2.0, __import__("math").radians(10.0))
    >>> round(m2, 3)
    2.385
    >>> p0_ratio
    1.0

    """
    if mach1 < 1:
        raise InvalidMachNumberError(mach1, reason="expansion fans require M1 >= 1")
    if turn_angle <= 0:
        raise ValueError(f"turn_angle must be positive (radians), got {turn_angle!r}")

    nu1 = prandtl_meyer_angle(mach1, gamma=gamma)
    g = gamma
    nu_max = (math.pi / 2) * (((g + 1) / (g - 1)) ** 0.5 - 1)
    nu2 = nu1 + turn_angle
    if nu2 >= nu_max:
        raise DetachedShockError(mach1=mach1, deflection=turn_angle, theta_max=nu_max - nu1)
    mach2 = mach_from_prandtl_meyer_angle(nu2, gamma=gamma)
    return mach2, 1.0
