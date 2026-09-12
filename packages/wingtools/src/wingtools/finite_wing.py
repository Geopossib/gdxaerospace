"""Finite-wing lift-curve-slope correction, induced drag, and Oswald efficiency.

Reference
---------
- Anderson, J.D., *Fundamentals of Aerodynamics*, 6th ed., Ch. 5
  (finite-wing theory, Eqs. 5.61-5.72).
- Helmbold's equation for low-aspect-ratio wings: Helmbold, H.B. (1942), a
  refinement of the classic Prandtl lifting-line result that remains
  accurate down to AR ~ 4 (Anderson Eq. 5.68).
- Raymer, D.P., *Aircraft Design: A Conceptual Approach*, 6th ed., Eq. 12.48
  for the Oswald efficiency factor estimate used here (straight, unswept
  wings).

Assumptions
-----------
- Subsonic, incompressible flow; no compressibility (Prandtl-Glauert)
  correction is applied here.
- The Oswald-efficiency estimate is a simplified empirical correlation for
  straight wings — swept-wing and highly non-elliptical planforms will be
  less accurate; see the docstring of ``oswald_efficiency_estimate`` for
  its stated validity range.
"""

from __future__ import annotations

import math

from wingtools.exceptions import InvalidWingGeometryError


def finite_wing_lift_curve_slope(
    lift_curve_slope_2d: float, aspect_ratio: float, *, model: str = "helmbold"
) -> float:
    """Finite-wing lift-curve slope from the 2D (airfoil) lift-curve slope.

    Parameters
    ----------
    lift_curve_slope_2d:
        Airfoil (infinite-wing) lift-curve slope, per radian
        (theoretically ``2*pi`` for thin-airfoil theory).
    aspect_ratio:
        Wing aspect ratio ``AR = b^2 / S``, > 0.
    model:
        ``"prandtl"``: classic lifting-line result,
        ``a = a0 / (1 + a0/(pi*AR))``, assumes an elliptical lift
        distribution (span efficiency e=1).
        ``"helmbold"`` (default): refinement that remains accurate for
        lower aspect ratios (down to AR ~ 4), Anderson Eq. 5.68.

    Returns
    -------
    float
        3D (finite-wing) lift-curve slope, per radian.

    Raises
    ------
    InvalidWingGeometryError
        If ``aspect_ratio`` is not positive.

    Example
    -------
    >>> import math
    >>> round(finite_wing_lift_curve_slope(2 * math.pi, aspect_ratio=8.0), 3)
    4.906

    """
    if aspect_ratio <= 0:
        raise InvalidWingGeometryError(f"aspect_ratio must be positive, got {aspect_ratio!r}")
    a0 = lift_curve_slope_2d
    if model == "prandtl":
        return a0 / (1 + a0 / (math.pi * aspect_ratio))
    if model == "helmbold":
        return a0 / (
            math.sqrt(1 + (a0 / (math.pi * aspect_ratio)) ** 2) + a0 / (math.pi * aspect_ratio)
        )
    raise InvalidWingGeometryError(
        f"Unknown model {model!r}; expected 'prandtl' or 'helmbold'."
    )


def oswald_efficiency_estimate(aspect_ratio: float, *, sweep_angle: float = 0.0) -> float:
    """Empirical Oswald span-efficiency factor for a straight or swept wing.

    Uses the Raymer correlation ``e = 1.78*(1-0.045*AR^0.68) - 0.64`` for
    unswept wings, blended toward the Kroo swept-wing correlation
    ``e = 4.61*(1-0.045*AR^0.68)*cos(sweep)^0.15 - 3.1`` as ``sweep_angle``
    increases past 30 degrees (both from Raymer Eq. 12.48-12.49).

    Parameters
    ----------
    aspect_ratio:
        Wing aspect ratio, > 0. Correlation is calibrated for AR in
        roughly 4-12.
    sweep_angle:
        Quarter-chord sweep angle, radians. Defaults to 0 (straight wing).

    Returns
    -------
    float
        Estimated Oswald efficiency factor, typically 0.7-0.9.

    Example
    -------
    >>> round(oswald_efficiency_estimate(aspect_ratio=8.0), 3)
    0.811

    """
    if aspect_ratio <= 0:
        raise InvalidWingGeometryError(f"aspect_ratio must be positive, got {aspect_ratio!r}")
    sweep_deg = math.degrees(sweep_angle)
    if sweep_deg <= 30:
        return float(1.78 * (1 - 0.045 * aspect_ratio**0.68) - 0.64)
    return float(4.61 * (1 - 0.045 * aspect_ratio**0.68) * math.cos(sweep_angle) ** 0.15 - 3.1)


def induced_drag_coefficient(
    lift_coefficient: float, aspect_ratio: float, *, oswald_efficiency: float = 1.0
) -> float:
    """Induced (lift-dependent) drag coefficient ``CDi = CL^2 / (pi * e * AR)``.

    Parameters
    ----------
    lift_coefficient:
        Wing lift coefficient ``CL``.
    aspect_ratio:
        Wing aspect ratio, > 0.
    oswald_efficiency:
        Span efficiency factor ``e``, in ``(0, 1]``. Defaults to 1.0 (ideal
        elliptical lift distribution — the minimum possible induced drag
        for a given AR and CL).

    Returns
    -------
    float
        Induced drag coefficient ``CDi``.

    Example
    -------
    >>> round(
    ...     induced_drag_coefficient(
    ...         lift_coefficient=0.5, aspect_ratio=8.0, oswald_efficiency=0.85
    ...     ),
    ...     5,
    ... )
    0.0117

    """
    if aspect_ratio <= 0:
        raise InvalidWingGeometryError(f"aspect_ratio must be positive, got {aspect_ratio!r}")
    if not (0 < oswald_efficiency <= 1):
        raise InvalidWingGeometryError(
            f"oswald_efficiency must be in (0, 1], got {oswald_efficiency!r}"
        )
    return lift_coefficient**2 / (math.pi * oswald_efficiency * aspect_ratio)
