"""Eclipse fraction for a circular orbit, cylindrical Earth-shadow model.

Reference
---------
- Vallado, D.A., *Fundamentals of Astrodynamics and Applications*, 4th
  ed., Ch. 5 (cylindrical shadow model).
- Wertz, J.R. & Larson, W.J. (eds.), *Space Mission Analysis and
  Design* (SMAD), 3rd ed., Ch. 6, for the same model in mission-design
  terms.

Assumptions
-----------
- Cylindrical shadow model: the sun is treated as infinitely far away
  (parallel rays), so Earth's shadow is a cylinder of Earth's radius
  rather than the slightly narrower umbra cone a point-source-corrected
  model would give. This is the standard first-order approximation for
  mission-design-level eclipse estimates; it slightly overestimates
  eclipse duration relative to the true (conical) umbra/penumbra
  geometry.
- Circular orbit only.
- ``beta_angle`` is the angle between the orbital plane and the
  Earth-Sun line; ``beta_angle = 0`` gives the maximum (worst-case)
  eclipse fraction for a given altitude.
"""

from __future__ import annotations

import math

from orbitpy.constants import EARTH_RADIUS

from missionpy.exceptions import InvalidMissionInputError


def eclipse_fraction(
    orbit_radius: float, *, beta_angle: float = 0.0, earth_radius: float = EARTH_RADIUS
) -> float:
    """Fraction of a circular orbit spent in Earth's (cylindrical) shadow.

    Parameters
    ----------
    orbit_radius:
        Circular orbit radius (from Earth's center), m, > ``earth_radius``.
    beta_angle:
        Angle between the orbital plane and the Earth-Sun line, radians,
        in ``[0, pi/2]``. Defaults to 0 (worst case: maximum eclipse).
    earth_radius:
        Earth (or other central body) radius, m.

    Returns
    -------
    float
        Fraction of the orbit period spent in shadow, in ``[0, 1)``. A
        beta angle large enough that the orbit never enters the shadow
        cylinder returns exactly 0.

    Example
    -------
    A typical 400 km altitude LEO spends nearly 40% of each orbit in
    eclipse at beta=0 (worst case), consistent with the commonly cited
    mission-design rule of thumb of roughly a third to 40%:

    >>> round(eclipse_fraction(orbit_radius=6_778_000.0), 3)
    0.39

    """
    if orbit_radius <= earth_radius:
        raise InvalidMissionInputError(
            f"orbit_radius ({orbit_radius!r}) must exceed earth_radius ({earth_radius!r})"
        )
    if not (0 <= beta_angle <= math.pi / 2):
        raise InvalidMissionInputError(f"beta_angle must be in [0, pi/2], got {beta_angle!r}")

    cos_beta = math.cos(beta_angle)
    if cos_beta < 1e-12:
        return 0.0  # orbital plane edge-on to the sun-line: never in shadow

    term = math.sqrt(orbit_radius**2 - earth_radius**2) / (orbit_radius * cos_beta)
    if term >= 1.0:
        return 0.0  # beta angle large enough that the orbit clears the shadow cylinder
    return math.acos(term) / math.pi


def eclipse_duration(
    orbit_radius: float,
    orbital_period: float,
    *,
    beta_angle: float = 0.0,
    earth_radius: float = EARTH_RADIUS,
) -> float:
    """Duration of a circular orbit's eclipse per revolution.

    Parameters
    ----------
    orbit_radius:
        Circular orbit radius, m, > ``earth_radius``.
    orbital_period:
        Orbital period, s, > 0 (see :func:`orbitpy.orbital_period`).
    beta_angle:
        See :func:`eclipse_fraction`.
    earth_radius:
        Earth (or other central body) radius, m.

    Returns
    -------
    float
        Eclipse duration, s.

    Example
    -------
    >>> from orbitpy import orbital_period
    >>> period = orbital_period(6_778_000.0)
    >>> round(eclipse_duration(6_778_000.0, period) / 60, 1)
    36.1

    """
    if orbital_period <= 0:
        raise InvalidMissionInputError(
            f"orbital_period must be positive, got {orbital_period!r}"
        )
    fraction = eclipse_fraction(orbit_radius, beta_angle=beta_angle, earth_radius=earth_radius)
    return fraction * orbital_period
