"""Conversions between classical orbital elements and Cartesian state vectors.

Reference
---------
- Vallado, D.A., *Fundamentals of Astrodynamics and Applications*, 4th
  ed., Algorithm 10 (COE to RV) and Algorithm 9 (RV to COE).

Convention
----------
- Cartesian state vectors are in an inertial frame (e.g. ECI/GCRF); this
  module does not care which specific inertial frame, only that it is
  inertial and centered on the body with gravitational parameter ``mu``.
- Classical orbital elements: semi-major axis ``a`` (m), eccentricity
  ``e``, inclination ``i`` (rad), right ascension of ascending node
  ``raan`` (rad), argument of periapsis ``argp`` (rad), true anomaly
  ``nu`` (rad).
- Only elliptical orbits (0 <= e < 1) are supported; equatorial
  (i=0) and circular (e=0) orbits have degenerate raan/argp
  respectively, which this module does not special-case (it will return
  raan=0 or argp=0 by convention in those cases, per the underlying
  vector-angle formulas).
"""

from __future__ import annotations

import math

import numpy as np

from orbitpy.constants import EARTH_MU
from orbitpy.exceptions import InvalidOrbitError

_TWO_PI = 2 * math.pi


def kepler_to_cartesian(
    semi_major_axis: float,
    eccentricity: float,
    inclination: float,
    raan: float,
    argp: float,
    true_anomaly: float,
    *,
    mu: float = EARTH_MU,
) -> tuple[np.ndarray, np.ndarray]:
    """Convert classical orbital elements to an inertial-frame Cartesian state vector.

    Parameters
    ----------
    semi_major_axis:
        Semi-major axis, m, > 0.
    eccentricity:
        Eccentricity, in ``[0, 1)``.
    inclination:
        Inclination, radians, in ``[0, pi]``.
    raan:
        Right ascension of the ascending node, radians.
    argp:
        Argument of periapsis, radians.
    true_anomaly:
        True anomaly, radians.
    mu:
        Gravitational parameter, m^3/s^2.

    Returns
    -------
    (position, velocity):
        Inertial-frame position (m) and velocity (m/s), each shape ``(3,)``.

    Example
    -------
    A circular, equatorial orbit at radius 7,000 km should have velocity
    purely in the y-direction when starting on the +x axis:

    >>> import numpy as np
    >>> r, v = kepler_to_cartesian(7_000_000.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    >>> np.round(r, 1)
    array([7000000.,       0.,       0.])
    >>> round(float(np.linalg.norm(v)), 1)
    7546.1

    """
    if semi_major_axis <= 0:
        raise InvalidOrbitError(f"semi_major_axis must be positive, got {semi_major_axis!r}")
    if not (0 <= eccentricity < 1):
        raise InvalidOrbitError(f"eccentricity must be in [0, 1), got {eccentricity!r}")
    if not (0 <= inclination <= math.pi):
        raise InvalidOrbitError(f"inclination must be in [0, pi], got {inclination!r}")

    p = semi_major_axis * (1 - eccentricity**2)
    r_mag = p / (1 + eccentricity * math.cos(true_anomaly))

    r_pqw = np.array([r_mag * math.cos(true_anomaly), r_mag * math.sin(true_anomaly), 0.0])
    v_pqw = np.array(
        [
            -math.sqrt(mu / p) * math.sin(true_anomaly),
            math.sqrt(mu / p) * (eccentricity + math.cos(true_anomaly)),
            0.0,
        ]
    )

    cos_o, sin_o = math.cos(raan), math.sin(raan)
    cos_i, sin_i = math.cos(inclination), math.sin(inclination)
    cos_w, sin_w = math.cos(argp), math.sin(argp)

    rotation = np.array(
        [
            [
                cos_o * cos_w - sin_o * sin_w * cos_i,
                -cos_o * sin_w - sin_o * cos_w * cos_i,
                sin_o * sin_i,
            ],
            [
                sin_o * cos_w + cos_o * sin_w * cos_i,
                -sin_o * sin_w + cos_o * cos_w * cos_i,
                -cos_o * sin_i,
            ],
            [sin_w * sin_i, cos_w * sin_i, cos_i],
        ]
    )

    position = rotation @ r_pqw
    velocity = rotation @ v_pqw
    return position, velocity


def cartesian_to_kepler(
    position: np.ndarray, velocity: np.ndarray, *, mu: float = EARTH_MU
) -> tuple[float, float, float, float, float, float]:
    """Convert an inertial-frame Cartesian state vector to classical orbital elements.

    Parameters
    ----------
    position:
        Inertial-frame position, m, shape ``(3,)``.
    velocity:
        Inertial-frame velocity, m/s, shape ``(3,)``.
    mu:
        Gravitational parameter, m^3/s^2.

    Returns
    -------
    (a, e, i, raan, argp, nu):
        Semi-major axis (m), eccentricity, inclination (rad), RAAN (rad),
        argument of periapsis (rad), true anomaly (rad).

    Raises
    ------
    InvalidOrbitError
        If the resulting orbit is not a closed ellipse (e >= 1), which
        this module does not support, or if ``position``/``velocity``
        have the wrong shape.

    Example
    -------
    >>> import numpy as np
    >>> r = np.array([7_000_000.0, 0.0, 0.0])
    >>> v = np.array([0.0, 7546.053, 0.0])
    >>> a, e, i, raan, argp, nu = cartesian_to_kepler(r, v)
    >>> round(a, 0), round(e, 5)
    (6999999.0, 0.0)

    """
    r = np.asarray(position, dtype=float)
    v = np.asarray(velocity, dtype=float)
    if r.shape != (3,) or v.shape != (3,):
        raise InvalidOrbitError("position and velocity must each have shape (3,)")

    r_mag = float(np.linalg.norm(r))
    v_mag = float(np.linalg.norm(v))
    if r_mag < 1e-6:
        raise InvalidOrbitError("position must not be (near) the origin")

    h_vec = np.cross(r, v)
    h_mag = float(np.linalg.norm(h_vec))
    n_vec = np.cross(np.array([0.0, 0.0, 1.0]), h_vec)
    n_mag = float(np.linalg.norm(n_vec))

    e_vec = (np.cross(v, h_vec) / mu) - r / r_mag
    e = float(np.linalg.norm(e_vec))
    if e >= 1:
        raise InvalidOrbitError(
            f"orbit is not elliptical (e={e:.6f} >= 1); parabolic/hyperbolic orbits "
            "are not supported by this module"
        )

    energy = v_mag**2 / 2 - mu / r_mag
    a = -mu / (2 * energy)

    i = math.acos(max(-1.0, min(1.0, h_vec[2] / h_mag)))

    if n_mag < 1e-9:
        raan = 0.0  # equatorial orbit: RAAN undefined, use 0 by convention
    else:
        raan = math.acos(max(-1.0, min(1.0, n_vec[0] / n_mag)))
        if n_vec[1] < 0:
            raan = _TWO_PI - raan

    if e < 1e-9:
        argp = 0.0  # circular orbit: argument of periapsis undefined, use 0 by convention
    elif n_mag < 1e-9:
        argp = math.atan2(e_vec[1], e_vec[0])
        if h_vec[2] < 0:
            argp = _TWO_PI - argp
    else:
        argp = math.acos(max(-1.0, min(1.0, float(n_vec @ e_vec) / (n_mag * e))))
        if e_vec[2] < 0:
            argp = _TWO_PI - argp

    if e < 1e-9:
        # For a circular orbit, reference the true anomaly from the node (or x-axis if
        # equatorial) rather than from a periapsis direction that doesn't exist.
        ref_vec = n_vec if n_mag >= 1e-9 else np.array([1.0, 0.0, 0.0])
        ref_mag = n_mag if n_mag >= 1e-9 else 1.0
        nu = math.acos(max(-1.0, min(1.0, float(ref_vec @ r) / (ref_mag * r_mag))))
        if r[2] < 0:
            nu = _TWO_PI - nu
    else:
        nu = math.acos(max(-1.0, min(1.0, float(e_vec @ r) / (e * r_mag))))
        if float(r @ v) < 0:
            nu = _TWO_PI - nu

    return a, e, i, raan, argp, nu
