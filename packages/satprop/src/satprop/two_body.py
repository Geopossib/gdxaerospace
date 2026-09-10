"""Two-body (Keplerian) propagation of a Cartesian state vector.

Reference
---------
- Vallado, D.A., *Fundamentals of Astrodynamics and Applications*, 4th
  ed., Ch. 2 (analytic two-body propagation via Kepler's equation).

Assumptions
-----------
- Pure two-body dynamics (point-mass gravity, no perturbations) --
  suitable for mission-design-level analysis of a hypothetical orbit,
  not for propagating real tracking data (use :func:`satprop.propagate_tle`
  and a current TLE for that).
- Elliptical orbits only (0 <= e < 1); this module does not handle
  parabolic or hyperbolic trajectories.
"""

from __future__ import annotations

import math

import numpy as np
from orbitpy.constants import EARTH_MU
from orbitpy.elements import cartesian_to_kepler, kepler_to_cartesian
from orbitpy.kepler import (
    eccentric_anomaly_from_true,
    solve_kepler_equation,
    true_anomaly_from_eccentric,
)

from satprop.exceptions import PropagationError


def two_body_propagate(
    position: np.ndarray, velocity: np.ndarray, delta_t: float, *, mu: float = EARTH_MU
) -> tuple[np.ndarray, np.ndarray]:
    """Analytically propagate a two-body orbit forward (or backward) by ``delta_t``.

    Converts the state to orbital elements, advances the mean anomaly
    linearly (exact for the unperturbed two-body problem), solves
    Kepler's equation for the new eccentric/true anomaly, and converts
    back to a Cartesian state.

    Parameters
    ----------
    position:
        Initial inertial-frame position, m, shape ``(3,)``.
    velocity:
        Initial inertial-frame velocity, m/s, shape ``(3,)``.
    delta_t:
        Propagation time, s (negative propagates backward in time).
    mu:
        Gravitational parameter, m^3/s^2.

    Returns
    -------
    (position, velocity):
        Propagated state, m and m/s, each shape ``(3,)``.

    Raises
    ------
    PropagationError
        If the initial state does not correspond to an elliptical orbit.

    Example
    -------
    Propagating a circular orbit forward by exactly one full period
    should return (very nearly) to the starting position:

    >>> import numpy as np
    >>> from orbitpy import circular_velocity, orbital_period
    >>> r0 = np.array([7_000_000.0, 0.0, 0.0])
    >>> v0 = np.array([0.0, circular_velocity(7_000_000.0), 0.0])
    >>> period = orbital_period(7_000_000.0)
    >>> r1, v1 = two_body_propagate(r0, v0, period)
    >>> np.allclose(r0, r1, atol=1.0)
    True

    """
    try:
        a, e, i, raan, argp, nu0 = cartesian_to_kepler(position, velocity, mu=mu)
    except Exception as exc:  # noqa: BLE001 - re-raise as this module's own error type
        raise PropagationError(f"cannot propagate: {exc}") from exc

    n = math.sqrt(mu / a**3)  # mean motion, rad/s
    e0 = eccentric_anomaly_from_true(nu0, e)
    m0 = e0 - e * math.sin(e0)

    m1 = m0 + n * delta_t
    e1 = solve_kepler_equation(m1, e)
    nu1 = true_anomaly_from_eccentric(e1, e)

    return kepler_to_cartesian(a, e, i, raan, argp, nu1, mu=mu)
