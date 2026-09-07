"""NACA 4-digit airfoil geometry.

Reference
---------
- Abbott, I.H. & Von Doenhoff, A.E., *Theory of Wing Sections*, Dover, 1959,
  Ch. 6 (equations for the NACA four-digit series).
- Moran, J., *An Introduction to Theoretical and Computational Aerodynamics*,
  Appendix A.

Assumptions
-----------
- Standard closed-trailing-edge thickness polynomial (a4 = -0.1015). Set
  ``closed_trailing_edge=False`` for the classic open-TE coefficients used in
  some older references (a4 = -0.1036).
- Camber line is the standard two-segment parabolic-arc NACA 4-digit
  definition; it is only C1-continuous at ``x = p*c`` (matches the slope but
  not curvature), as in the original NACA reports.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from airfoilpy.exceptions import InvalidAirfoilCodeError

# Thickness-distribution coefficients (Abbott & Von Doenhoff, Eq. 6.2).
_A0 = 0.2969
_A1 = -0.1260
_A2 = -0.3516
_A3 = 0.2843
_A4_CLOSED = -0.1015
_A4_OPEN = -0.1036


def _parse_naca4(code: str) -> tuple[float, float, float]:
    digits = code.strip().upper().removeprefix("NACA").strip()
    if len(digits) != 4 or not digits.isdigit():
        raise InvalidAirfoilCodeError(code, expected="4-digit NACA code, e.g. '2412' or '0012'")
    m = int(digits[0]) / 100.0
    p = int(digits[1]) / 10.0
    t = int(digits[2:4]) / 100.0
    return m, p, t


def naca4_thickness(
    x: np.ndarray, thickness: float, *, closed_trailing_edge: bool = True
) -> np.ndarray:
    """Half-thickness distribution ``y_t(x)`` for the NACA 4-digit series.

    Parameters
    ----------
    x:
        Chordwise stations, normalized by chord, in ``[0, 1]``.
    thickness:
        Maximum thickness as a fraction of chord (e.g. ``0.12`` for 12%).
    closed_trailing_edge:
        If True (default), uses the coefficient set that closes the
        trailing edge exactly at ``x = 1``. If False, uses the original
        open-TE coefficients from the NACA reports.

    Returns
    -------
    numpy.ndarray
        Half-thickness ``y_t`` at each station, same shape as ``x``.

    """
    x = np.asarray(x, dtype=float)
    if np.any((x < 0) | (x > 1)):
        raise ValueError("x stations must lie in [0, 1] (normalized chord).")
    a4 = _A4_CLOSED if closed_trailing_edge else _A4_OPEN
    return (
        5 * thickness
        * (_A0 * np.sqrt(x) + _A1 * x + _A2 * x**2 + _A3 * x**3 + a4 * x**4)
    )


def naca4_camber(
    x: np.ndarray, max_camber: float, camber_position: float
) -> tuple[np.ndarray, np.ndarray]:
    """Mean camber line ``y_c(x)`` and its slope ``dy_c/dx`` for NACA 4-digit.

    Parameters
    ----------
    x:
        Chordwise stations, normalized by chord, in ``[0, 1]``.
    max_camber:
        Maximum camber as a fraction of chord (the first NACA digit / 100).
    camber_position:
        Chordwise location of maximum camber, as a fraction of chord (the
        second NACA digit / 10).

    Returns
    -------
    (yc, dyc_dx):
        Camber-line ordinate and slope at each station.

    """
    x = np.asarray(x, dtype=float)
    m, p = max_camber, camber_position
    yc = np.zeros_like(x)
    dyc = np.zeros_like(x)

    if m == 0.0 or p == 0.0:
        return yc, dyc  # symmetric airfoil: zero camber everywhere

    fwd = x <= p
    aft = ~fwd

    yc[fwd] = (m / p**2) * (2 * p * x[fwd] - x[fwd] ** 2)
    dyc[fwd] = (2 * m / p**2) * (p - x[fwd])

    yc[aft] = (m / (1 - p) ** 2) * ((1 - 2 * p) + 2 * p * x[aft] - x[aft] ** 2)
    dyc[aft] = (2 * m / (1 - p) ** 2) * (p - x[aft])

    return yc, dyc


@dataclass(frozen=True)
class AirfoilCoordinates:
    """Upper/lower surface coordinates of an airfoil, normalized by chord."""

    x_upper: np.ndarray
    y_upper: np.ndarray
    x_lower: np.ndarray
    y_lower: np.ndarray


def naca4_coordinates(
    code: str, *, n_points: int = 100, closed_trailing_edge: bool = True
) -> AirfoilCoordinates:
    """Generate upper/lower surface coordinates for a NACA 4-digit airfoil.

    Parameters
    ----------
    code:
        Four-digit NACA designation, e.g. ``"2412"`` or ``"NACA0012"``.
    n_points:
        Number of chordwise stations. Cosine spacing is used to cluster
        points near the leading and trailing edges, as is standard practice.
    closed_trailing_edge:
        See :func:`naca4_thickness`.

    Returns
    -------
    AirfoilCoordinates

    Raises
    ------
    InvalidAirfoilCodeError
        If ``code`` is not a valid 4-digit NACA designation.

    Example
    -------
    >>> coords = naca4_coordinates("0012", n_points=10)
    >>> round(float(coords.y_upper.max()), 3)  # ~half of 0.12 max thickness
    0.059

    """
    m, p, t = _parse_naca4(code)
    beta = np.linspace(0, np.pi, n_points)
    x = (1 - np.cos(beta)) / 2  # cosine spacing, clusters near LE/TE

    yt = naca4_thickness(x, t, closed_trailing_edge=closed_trailing_edge)
    yc, dyc = naca4_camber(x, m, p)
    theta = np.arctan(dyc)

    x_upper = x - yt * np.sin(theta)
    y_upper = yc + yt * np.cos(theta)
    x_lower = x + yt * np.sin(theta)
    y_lower = yc - yt * np.cos(theta)

    return AirfoilCoordinates(x_upper, y_upper, x_lower, y_lower)
