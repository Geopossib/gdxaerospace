"""Fundamental two-body (Keplerian) orbit relations.

Reference
---------
- Vallado, D.A., *Fundamentals of Astrodynamics and Applications*, 4th
  ed., Ch. 1-2 (vis-viva equation, orbital period, Kepler's equation and
  its solution).
- Curtis, H.D., *Orbital Mechanics for Engineering Students*, 3rd ed.,
  Ch. 2-3, for the same relations in a slightly different notation.

Assumptions
-----------
- Two-body problem only: a single central body, point-mass gravity, no
  perturbations (J2, drag, third-body, SRP). For perturbed propagation
  from real tracking data, see ``satprop`` (which wraps SGP4).
"""

from __future__ import annotations

import math

from orbitpy.constants import EARTH_MU
from orbitpy.exceptions import InvalidOrbitError, OrbitSolverConvergenceError


def orbital_period(semi_major_axis: float, *, mu: float = EARTH_MU) -> float:
    """Orbital period: ``T = 2*pi*sqrt(a^3/mu)``.

    Parameters
    ----------
    semi_major_axis:
        Semi-major axis, m, > 0.
    mu:
        Gravitational parameter of the central body, m^3/s^2.

    Returns
    -------
    float
        Orbital period, s.

    Example
    -------
    >>> round(orbital_period(6_778_000.0) / 60, 2)
    92.56

    """
    if semi_major_axis <= 0:
        raise InvalidOrbitError(f"semi_major_axis must be positive, got {semi_major_axis!r}")
    return 2 * math.pi * math.sqrt(semi_major_axis**3 / mu)


def circular_velocity(radius: float, *, mu: float = EARTH_MU) -> float:
    """Circular orbital velocity: ``v = sqrt(mu/r)``.

    Parameters
    ----------
    radius:
        Orbital radius, m, > 0.
    mu:
        Gravitational parameter, m^3/s^2.

    Example
    -------
    >>> round(circular_velocity(6_778_000.0), 1)
    7668.6

    """
    if radius <= 0:
        raise InvalidOrbitError(f"radius must be positive, got {radius!r}")
    return math.sqrt(mu / radius)


def escape_velocity(radius: float, *, mu: float = EARTH_MU) -> float:
    """Escape velocity: ``v = sqrt(2*mu/r)``.

    Example:
    -------
    >>> round(escape_velocity(6_378_137.0), 1)
    11179.9

    """
    if radius <= 0:
        raise InvalidOrbitError(f"radius must be positive, got {radius!r}")
    return math.sqrt(2 * mu / radius)


def vis_viva_speed(radius: float, semi_major_axis: float, *, mu: float = EARTH_MU) -> float:
    """Vis-viva equation: ``v = sqrt(mu*(2/r - 1/a))``.

    Parameters
    ----------
    radius:
        Current orbital radius, m, > 0.
    semi_major_axis:
        Orbit semi-major axis, m (> 0 for ellipse/circle; negative for a
        hyperbolic orbit is accepted, since the formula holds generally).
    mu:
        Gravitational parameter, m^3/s^2.

    Returns
    -------
    float
        Speed at ``radius``, m/s.

    Example
    -------
    >>> round(vis_viva_speed(radius=7_000_000.0, semi_major_axis=7_000_000.0), 1)
    7546.1

    """
    if radius <= 0:
        raise InvalidOrbitError(f"radius must be positive, got {radius!r}")
    return math.sqrt(mu * (2 / radius - 1 / semi_major_axis))


def solve_kepler_equation(
    mean_anomaly: float,
    eccentricity: float,
    *,
    tolerance: float = 1e-12,
    max_iterations: int = 100,
) -> float:
    """Solve Kepler's equation ``M = E - e*sin(E)`` for eccentric anomaly ``E``.

    Solved by Newton-Raphson iteration from an initial guess of ``E0 = M``.

    Parameters
    ----------
    mean_anomaly:
        Mean anomaly, radians.
    eccentricity:
        Orbital eccentricity, in ``[0, 1)`` (elliptical orbits only).
    tolerance, max_iterations:
        Newton-Raphson convergence controls.

    Returns
    -------
    float
        Eccentric anomaly, radians.

    Raises
    ------
    InvalidOrbitError
        If ``eccentricity`` is outside ``[0, 1)``.
    OrbitSolverConvergenceError
        If Newton-Raphson fails to converge within ``max_iterations``.

    Example
    -------
    >>> round(solve_kepler_equation(mean_anomaly=1.0, eccentricity=0.1), 6)
    1.088598

    """
    if not (0 <= eccentricity < 1):
        raise InvalidOrbitError(f"eccentricity must be in [0, 1), got {eccentricity!r}")
    m = mean_anomaly % (2 * math.pi)
    e_anomaly = m
    for _ in range(max_iterations):
        f = e_anomaly - eccentricity * math.sin(e_anomaly) - m
        fprime = 1 - eccentricity * math.cos(e_anomaly)
        delta = f / fprime
        e_anomaly -= delta
        if abs(delta) < tolerance:
            return e_anomaly
    raise OrbitSolverConvergenceError("solve_kepler_equation", max_iterations, tolerance)


def true_anomaly_from_eccentric(eccentric_anomaly: float, eccentricity: float) -> float:
    """Convert eccentric anomaly to true anomaly.

    ``tan(nu/2) = sqrt((1+e)/(1-e)) * tan(E/2)``.

    Parameters
    ----------
    eccentric_anomaly:
        Eccentric anomaly, radians.
    eccentricity:
        Orbital eccentricity, in ``[0, 1)``.

    Returns
    -------
    float
        True anomaly, radians, in ``(-pi, pi]``.

    Example
    -------
    >>> E = solve_kepler_equation(mean_anomaly=1.0, eccentricity=0.1)
    >>> round(true_anomaly_from_eccentric(E, 0.1), 6)
    1.179469

    """
    if not (0 <= eccentricity < 1):
        raise InvalidOrbitError(f"eccentricity must be in [0, 1), got {eccentricity!r}")
    return 2 * math.atan2(
        math.sqrt(1 + eccentricity) * math.sin(eccentric_anomaly / 2),
        math.sqrt(1 - eccentricity) * math.cos(eccentric_anomaly / 2),
    )


def eccentric_anomaly_from_true(true_anomaly: float, eccentricity: float) -> float:
    """Convert true anomaly to eccentric anomaly (inverse of :func:`true_anomaly_from_eccentric`).

    Example:
    -------
    >>> nu = true_anomaly_from_eccentric(1.088598, 0.1)
    >>> round(eccentric_anomaly_from_true(nu, 0.1), 6)
    1.088598

    """
    if not (0 <= eccentricity < 1):
        raise InvalidOrbitError(f"eccentricity must be in [0, 1), got {eccentricity!r}")
    return 2 * math.atan2(
        math.sqrt(1 - eccentricity) * math.sin(true_anomaly / 2),
        math.sqrt(1 + eccentricity) * math.cos(true_anomaly / 2),
    )
