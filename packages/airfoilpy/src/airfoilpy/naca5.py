"""NACA 5-digit airfoil geometry (standard, non-reflexed camber line).

Reference
---------
- Abbott, I.H. & Von Doenhoff, A.E., *Theory of Wing Sections*, Dover, 1959,
  Ch. 6.
- Jacobs & Pinkerton, NACA Report No. 537 (1935), original 5-digit series.

Assumptions
-----------
- Only the standard (non-reflexed) 5-digit camber line is implemented; the
  design lift coefficient is restricted to Cl = 0.3 (the historical NACA
  5-digit series was defined only for this design Cl).
- Only the tabulated ``(p, m, k1)`` triples published by NACA for
  ``p in {1, 2, 3, 4, 5}`` (camber position 5%-25% chord) are supported.
- Thickness distribution is identical to the NACA 4-digit series
  (see :func:`airfoilpy.naca4.naca4_thickness`).
"""

from __future__ import annotations

import numpy as np

from airfoilpy.exceptions import InvalidAirfoilCodeError
from airfoilpy.naca4 import AirfoilCoordinates, naca4_thickness

# (p_code -> (camber_position_fraction, m, k1)), from NACA Report 537 / Abbott & Von Doenhoff Table.
# p_code is the second digit of the 5-digit designation (position of max camber in units of p/20).
_CAMBER_TABLE: dict[int, tuple[float, float, float]] = {
    1: (0.05, 0.0580, 361.4),
    2: (0.10, 0.1260, 51.64),
    3: (0.15, 0.2025, 15.957),
    4: (0.20, 0.2900, 6.643),
    5: (0.25, 0.3910, 3.230),
}


def _parse_naca5(code: str) -> tuple[int, int, float]:
    digits = code.strip().upper().removeprefix("NACA").strip()
    if len(digits) != 5 or not digits.isdigit():
        raise InvalidAirfoilCodeError(
            code, expected="5-digit NACA code, e.g. '23012'"
        )
    cl_design_digit = int(digits[0])  # Cl_design = 3/2 * digit / 10, restricted to digit=2 (Cl=0.3)
    p_code = int(digits[1])
    reflex_digit = int(digits[2])
    thickness = int(digits[3:5]) / 100.0

    if cl_design_digit != 2:
        raise InvalidAirfoilCodeError(
            code,
            expected=(
                "a first digit of '2' (design Cl = 0.3); this is the only "
                "design lift coefficient the historical NACA 5-digit series "
                "was published for"
            ),
        )
    if reflex_digit != 0:
        raise InvalidAirfoilCodeError(
            code, expected="a third digit of '0' (reflexed camber lines are not yet implemented)"
        )
    if p_code not in _CAMBER_TABLE:
        raise InvalidAirfoilCodeError(
            code, expected=f"second digit in {sorted(_CAMBER_TABLE)} (published camber positions)"
        )
    return p_code, reflex_digit, thickness


def naca5_camber(x: np.ndarray, p_code: int) -> tuple[np.ndarray, np.ndarray]:
    """Compute the standard NACA 5-digit mean camber line and its slope.

    Parameters
    ----------
    x:
        Chordwise stations, normalized by chord, in ``[0, 1]``.
    p_code:
        Second digit of the 5-digit designation (1-5), selecting the
        published ``(m, k1)`` pair for that camber position.

    Returns
    -------
    (yc, dyc_dx)

    """
    x = np.asarray(x, dtype=float)
    _, m, k1 = _CAMBER_TABLE[p_code]

    yc = np.zeros_like(x)
    dyc = np.zeros_like(x)

    fwd = x <= m
    aft = ~fwd

    yc[fwd] = (k1 / 6) * (x[fwd] ** 3 - 3 * m * x[fwd] ** 2 + m**2 * (3 - m) * x[fwd])
    dyc[fwd] = (k1 / 6) * (3 * x[fwd] ** 2 - 6 * m * x[fwd] + m**2 * (3 - m))

    yc[aft] = (k1 * m**3 / 6) * (1 - x[aft])
    dyc[aft] = -(k1 * m**3 / 6) * np.ones_like(x[aft])

    return yc, dyc


def naca5_coordinates(code: str, *, n_points: int = 100) -> AirfoilCoordinates:
    """Generate upper/lower surface coordinates for a standard NACA 5-digit airfoil.

    Parameters
    ----------
    code:
        Five-digit NACA designation with design Cl = 0.3 and no reflex,
        e.g. ``"23012"``.
    n_points:
        Number of chordwise stations (cosine-spaced).

    Returns
    -------
    AirfoilCoordinates

    Raises
    ------
    InvalidAirfoilCodeError
        If ``code`` is not a supported 5-digit NACA designation.

    Example
    -------
    >>> coords = naca5_coordinates("23012", n_points=10)
    >>> coords.y_upper.shape
    (10,)

    """
    p_code, _, thickness = _parse_naca5(code)
    beta = np.linspace(0, np.pi, n_points)
    x = (1 - np.cos(beta)) / 2

    yt = naca4_thickness(x, thickness)
    yc, dyc = naca5_camber(x, p_code)
    theta = np.arctan(dyc)

    x_upper = x - yt * np.sin(theta)
    y_upper = yc + yt * np.cos(theta)
    x_lower = x + yt * np.sin(theta)
    y_lower = yc - yt * np.cos(theta)

    return AirfoilCoordinates(x_upper, y_upper, x_lower, y_lower)
