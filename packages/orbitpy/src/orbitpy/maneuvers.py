"""Impulsive orbital maneuvers: Hohmann transfer, bi-elliptic transfer, plane change.

Reference
---------
- Vallado, D.A., *Fundamentals of Astrodynamics and Applications*, 4th
  ed., Ch. 6 (Hohmann transfer Eq. 6-1 to 6-4; bi-elliptic transfer
  Eq. 6-5 to 6-9; combined plane-change formula Eq. 6-16).
- Curtis, H.D., *Orbital Mechanics for Engineering Students*, 3rd ed.,
  Ch. 6, for the same relations.

Assumptions
-----------
- All maneuvers are impulsive (instantaneous velocity change, zero burn
  duration) -- a standard simplifying assumption for delta-v budgeting
  that ignores finite-burn losses (gravity losses during the burn).
- Both orbits are assumed coplanar for the Hohmann/bi-elliptic transfers;
  a pure plane-change maneuver is handled separately by
  :func:`inclination_change_delta_v` (or combined via
  :func:`combined_plane_change_delta_v`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from orbitpy.constants import EARTH_MU
from orbitpy.exceptions import InvalidOrbitError
from orbitpy.kepler import orbital_period


@dataclass(frozen=True)
class HohmannTransferResult:
    """Result of a Hohmann transfer calculation."""

    delta_v1: float
    delta_v2: float
    total_delta_v: float
    transfer_time: float


def hohmann_transfer(r1: float, r2: float, *, mu: float = EARTH_MU) -> HohmannTransferResult:
    """Two-impulse Hohmann transfer between two coplanar circular orbits.

    Parameters
    ----------
    r1:
        Initial circular orbit radius, m, > 0.
    r2:
        Final circular orbit radius, m, > 0.
    mu:
        Gravitational parameter, m^3/s^2.

    Returns
    -------
    HohmannTransferResult

    Example
    -------
    LEO (300 km altitude) to GEO transfer, a well-known benchmark case:

    >>> result = hohmann_transfer(r1=6_678_000.0, r2=42_164_000.0)
    >>> round(result.delta_v1, 1)
    2425.8
    >>> round(result.delta_v2, 1)
    1466.8
    >>> round(result.transfer_time / 3600, 3)
    5.275

    """
    if r1 <= 0 or r2 <= 0:
        raise InvalidOrbitError(f"r1 and r2 must both be positive, got r1={r1!r}, r2={r2!r}")

    a_transfer = (r1 + r2) / 2
    v1_circular = math.sqrt(mu / r1)
    v2_circular = math.sqrt(mu / r2)
    v1_transfer = math.sqrt(mu * (2 / r1 - 1 / a_transfer))
    v2_transfer = math.sqrt(mu * (2 / r2 - 1 / a_transfer))

    delta_v1 = abs(v1_transfer - v1_circular)
    delta_v2 = abs(v2_circular - v2_transfer)
    transfer_time = orbital_period(a_transfer, mu=mu) / 2

    return HohmannTransferResult(
        delta_v1=delta_v1,
        delta_v2=delta_v2,
        total_delta_v=delta_v1 + delta_v2,
        transfer_time=transfer_time,
    )


@dataclass(frozen=True)
class BiellipticTransferResult:
    """Result of a bi-elliptic transfer calculation."""

    delta_v1: float
    delta_v2: float
    delta_v3: float
    total_delta_v: float
    transfer_time: float


def bielliptic_transfer(
    r1: float, r2: float, r_intermediate: float, *, mu: float = EARTH_MU
) -> BiellipticTransferResult:
    """Three-impulse bi-elliptic transfer via an intermediate apoapsis radius.

    For a sufficiently large ``r_intermediate`` (typically needed when
    ``r2/r1`` is large, roughly > 11.94, Vallado Sec. 6.3), this can use
    less total delta-v than a direct Hohmann transfer, at the cost of a
    much longer transfer time.

    Parameters
    ----------
    r1:
        Initial circular orbit radius, m, > 0.
    r2:
        Final circular orbit radius, m, > 0.
    r_intermediate:
        Intermediate transfer-ellipse apoapsis radius, m, must exceed
        both ``r1`` and ``r2``.
    mu:
        Gravitational parameter, m^3/s^2.

    Returns
    -------
    BiellipticTransferResult

    Example
    -------
    A large radius ratio (r2/r1 ~ 30, above Vallado's ~11.94 threshold)
    where bi-elliptic actually beats a direct Hohmann transfer
    (4075.0 m/s) on total delta-v, at the cost of a much longer transfer:

    >>> result = bielliptic_transfer(r1=6_678_000.0, r2=200_000_000.0, r_intermediate=300_000_000.0)
    >>> round(result.total_delta_v, 1)
    4005.7

    """
    if r1 <= 0 or r2 <= 0:
        raise InvalidOrbitError(f"r1 and r2 must both be positive, got r1={r1!r}, r2={r2!r}")
    if r_intermediate <= max(r1, r2):
        raise InvalidOrbitError(
            f"r_intermediate ({r_intermediate!r}) must exceed both r1 and r2"
        )

    a_transfer1 = (r1 + r_intermediate) / 2
    a_transfer2 = (r2 + r_intermediate) / 2

    v1_circular = math.sqrt(mu / r1)
    v1_transfer1 = math.sqrt(mu * (2 / r1 - 1 / a_transfer1))
    delta_v1 = abs(v1_transfer1 - v1_circular)

    v_apo_transfer1 = math.sqrt(mu * (2 / r_intermediate - 1 / a_transfer1))
    v_apo_transfer2 = math.sqrt(mu * (2 / r_intermediate - 1 / a_transfer2))
    delta_v2 = abs(v_apo_transfer2 - v_apo_transfer1)

    v2_transfer2 = math.sqrt(mu * (2 / r2 - 1 / a_transfer2))
    v2_circular = math.sqrt(mu / r2)
    delta_v3 = abs(v2_circular - v2_transfer2)

    transfer_time = orbital_period(a_transfer1, mu=mu) / 2 + orbital_period(a_transfer2, mu=mu) / 2

    return BiellipticTransferResult(
        delta_v1=delta_v1,
        delta_v2=delta_v2,
        delta_v3=delta_v3,
        total_delta_v=delta_v1 + delta_v2 + delta_v3,
        transfer_time=transfer_time,
    )


def inclination_change_delta_v(velocity: float, delta_inclination: float) -> float:
    """Delta-v for a pure plane-change (inclination-only) maneuver at fixed speed.

    ``dv = 2 * v * sin(delta_i / 2)``.

    Parameters
    ----------
    velocity:
        Orbital speed at the maneuver point, m/s, > 0.
    delta_inclination:
        Inclination change, radians.

    Returns
    -------
    float
        Required delta-v, m/s.

    Example
    -------
    >>> round(inclination_change_delta_v(velocity=7668.6, delta_inclination=0.5), 1)
    3794.5

    """
    if velocity <= 0:
        raise InvalidOrbitError(f"velocity must be positive, got {velocity!r}")
    return 2 * velocity * abs(math.sin(delta_inclination / 2))


def combined_plane_change_delta_v(
    v1: float, v2: float, delta_inclination: float
) -> float:
    """Delta-v for a combined speed-change-plus-plane-change maneuver.

    ``dv = sqrt(v1^2 + v2^2 - 2*v1*v2*cos(delta_i))`` (law of cosines on
    the velocity triangle) -- generally cheaper than performing a Hohmann
    transfer and a separate plane change sequentially.

    Parameters
    ----------
    v1, v2:
        Speeds before and after the maneuver, m/s, both > 0.
    delta_inclination:
        Inclination change, radians.

    Returns
    -------
    float
        Required delta-v, m/s.

    Example
    -------
    >>> round(combined_plane_change_delta_v(v1=10000.0, v2=1467.6, delta_inclination=0.0), 1)
    8532.4

    """
    if v1 <= 0 or v2 <= 0:
        raise InvalidOrbitError(f"v1 and v2 must both be positive, got v1={v1!r}, v2={v2!r}")
    return math.sqrt(v1**2 + v2**2 - 2 * v1 * v2 * math.cos(delta_inclination))
