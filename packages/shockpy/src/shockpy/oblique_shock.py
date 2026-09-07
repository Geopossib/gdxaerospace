"""Oblique shock relations (theta-beta-M) for a calorically perfect gas.

Reference
---------
- Anderson, J.D., *Fundamentals of Aerodynamics*, 6th ed., Ch. 9,
  Eq. 9.23 (theta-beta-M relation), Eqs. 9.15-9.16 (normal-component
  decomposition back onto the normal-shock relations).

Assumptions
-----------
- Calorically perfect gas, straight oblique shock, attached (not detached/bow).
- The upstream normal Mach component ``M1n = M1 * sin(beta)`` must exceed 1,
  or no shock solution exists.
- For a given (M1, deflection), two shock-angle solutions generally exist
  (weak and strong); this module returns the weak-shock solution by default,
  which is what is physically observed on most external aerodynamic
  surfaces.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from aerocalc.exceptions import InvalidMachNumberError
from compressibleflow.isentropic import GAMMA_AIR

from shockpy.exceptions import DetachedShockError
from shockpy.normal_shock import normal_shock


def theta_from_beta(mach1: float, beta: float, *, gamma: float = GAMMA_AIR) -> float:
    """Flow deflection angle ``theta`` for a given shock angle ``beta`` (theta-beta-M).

    Parameters
    ----------
    mach1:
        Upstream Mach number, > 1.
    beta:
        Shock wave angle, radians, measured from the upstream flow direction.
    gamma:
        Ratio of specific heats.

    Returns
    -------
    float
        Flow deflection angle ``theta``, radians.

    Example
    -------
    >>> import math
    >>> round(math.degrees(theta_from_beta(2.0, math.radians(40.0))), 1)
    10.6

    """
    if mach1 <= 1:
        raise InvalidMachNumberError(mach1, reason="oblique shocks require M1 > 1")
    m1sq = mach1**2
    numerator = m1sq * math.sin(beta) ** 2 - 1
    denominator = m1sq * (gamma + math.cos(2 * beta)) + 2
    tan_theta = 2 * (1 / math.tan(beta)) * numerator / denominator
    return math.atan(tan_theta)


@dataclass(frozen=True)
class ObliqueShockResult:
    """Result of an oblique-shock solve: shock angle plus downstream properties."""

    mach_upstream: float
    deflection_angle: float
    shock_angle: float
    mach_downstream: float
    pressure_ratio: float
    temperature_ratio: float
    density_ratio: float
    stagnation_pressure_ratio: float


def oblique_shock(
    mach1: float,
    deflection: float,
    *,
    gamma: float = GAMMA_AIR,
    weak: bool = True,
    tolerance: float = 1e-8,
    max_iterations: int = 200,
) -> ObliqueShockResult:
    """Solve the theta-beta-M relation for shock angle, then downstream properties.

    Given upstream Mach number and a (positive) flow deflection angle, finds
    the shock angle ``beta`` by bisection on :func:`theta_from_beta`, then
    applies the normal-shock relations to the normal Mach component.

    Parameters
    ----------
    mach1:
        Upstream Mach number, > 1.
    deflection:
        Flow deflection (turning) angle, radians, > 0.
    gamma:
        Ratio of specific heats.
    weak:
        If True (default), return the weak-shock solution (smaller beta,
        the physically observed one on most bodies). If False, return the
        strong-shock solution.
    tolerance, max_iterations:
        Bisection convergence controls.

    Returns
    -------
    ObliqueShockResult

    Raises
    ------
    DetachedShockError
        If ``deflection`` exceeds the maximum deflection angle possible for
        this ``mach1`` (the shock detaches and becomes a curved bow shock,
        which this module does not model).

    Example
    -------
    >>> result = oblique_shock(2.0, __import__("math").radians(10.0))
    >>> round(__import__("math").degrees(result.shock_angle), 1)
    39.3

    """
    if mach1 <= 1:
        raise InvalidMachNumberError(mach1, reason="oblique shocks require M1 > 1")
    if deflection <= 0:
        raise ValueError(f"deflection must be positive (radians), got {deflection!r}")

    mu = math.asin(1 / mach1)  # Mach angle: minimum possible beta (zero-strength shock)

    # theta(beta) rises from 0 at beta=mu to a maximum theta_max, then falls to 0 at beta=pi/2.
    # Locate the peak by ternary search, then bisect on the appropriate branch for weak/strong.
    lo, hi = mu + 1e-9, math.pi / 2 - 1e-9
    for _ in range(100):
        m1_ = lo + (hi - lo) / 3
        m2_ = hi - (hi - lo) / 3
        if theta_from_beta(mach1, m1_, gamma=gamma) < theta_from_beta(mach1, m2_, gamma=gamma):
            lo = m1_
        else:
            hi = m2_
    beta_at_theta_max = (lo + hi) / 2
    theta_max = theta_from_beta(mach1, beta_at_theta_max, gamma=gamma)

    if deflection > theta_max:
        raise DetachedShockError(mach1=mach1, deflection=deflection, theta_max=theta_max)

    if weak:
        beta_lo, beta_hi = mu, beta_at_theta_max
    else:
        beta_lo, beta_hi = beta_at_theta_max, math.pi / 2

    for _ in range(max_iterations):
        beta_mid = (beta_lo + beta_hi) / 2
        theta_mid = theta_from_beta(mach1, beta_mid, gamma=gamma)
        if abs(theta_mid - deflection) < tolerance:
            break
        # theta increases monotonically with beta on each branch.
        if theta_mid < deflection:
            beta_lo = beta_mid
        else:
            beta_hi = beta_mid
    beta = (beta_lo + beta_hi) / 2

    mach1n = mach1 * math.sin(beta)
    normal = normal_shock(mach1n, gamma=gamma)
    mach2 = normal.mach_downstream / math.sin(beta - deflection)

    return ObliqueShockResult(
        mach_upstream=mach1,
        deflection_angle=deflection,
        shock_angle=beta,
        mach_downstream=mach2,
        pressure_ratio=normal.pressure_ratio,
        temperature_ratio=normal.temperature_ratio,
        density_ratio=normal.density_ratio,
        stagnation_pressure_ratio=normal.stagnation_pressure_ratio,
    )
