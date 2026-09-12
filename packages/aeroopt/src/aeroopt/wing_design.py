"""Worked example: optimal wing aspect ratio trading induced drag against structural weight.

Reference
---------
- The induced-drag term uses :func:`wingtools.induced_drag_coefficient`
  (``CDi = CL^2/(pi*e*AR)``, Anderson's finite-wing theory). The
  structural-weight penalty is a simple, illustrative quadratic model
  (``k*AR^2``) representing the well-known qualitative fact that higher
  aspect ratio requires a longer, more slender (and so heavier for a
  given strength/stiffness) wing structure -- Raymer, D.P., *Aircraft
  Design: A Conceptual Approach*, 6th ed., Ch. 15, discusses this
  aspect-ratio/structural-weight tradeoff qualitatively, though the
  specific quadratic form and its coefficient here are simplified for
  a clean, well-posed worked example, not a validated structural-weight
  regression.

Assumptions
-----------
- Combining a drag coefficient and a structural "penalty" into one
  additive objective is a simplification (they aren't the same
  physical unit) -- meant to demonstrate a genuine tradeoff structure
  with a well-defined interior optimum, not a rigorous multidisciplinary
  weight/drag figure of merit. A real aircraft MDO study would carry
  weight and drag as separate objectives or convert both into a common
  currency (e.g. fuel burn or direct operating cost) before combining them.
"""

from __future__ import annotations

from wingtools.finite_wing import induced_drag_coefficient

from aeroopt.exceptions import OptimizationError
from aeroopt.optimize import OptimizationResult, minimize_scalar_bounded


def total_drag_with_structural_penalty(
    aspect_ratio: float,
    lift_coefficient: float,
    parasitic_drag_coefficient: float,
    *,
    oswald_efficiency: float = 0.85,
    structural_penalty_coefficient: float = 1e-4,
) -> float:
    """Compute a total "cost" combining induced drag, parasitic drag, and a structural penalty.

    ``cost(AR) = CD0 + CL^2/(pi*e*AR) + k*AR^2``.

    Parameters
    ----------
    aspect_ratio:
        Wing aspect ratio, > 0.
    lift_coefficient:
        Wing lift coefficient.
    parasitic_drag_coefficient:
        Parasitic (zero-lift) drag coefficient, assumed independent of
        aspect ratio for this simplified example.
    oswald_efficiency:
        Span efficiency factor, in ``(0, 1]``.
    structural_penalty_coefficient:
        The quadratic structural-weight penalty coefficient ``k``, >= 0
        (see the module docstring for what this represents and its
        limitations).

    Returns
    -------
    float
        Combined cost (dimensionless, same "units" as a drag coefficient
        plus the penalty term).

    Example
    -------
    >>> round(
    ...     total_drag_with_structural_penalty(
    ...         aspect_ratio=8.0, lift_coefficient=0.5, parasitic_drag_coefficient=0.02
    ...     ),
    ...     5,
    ... )
    0.0381

    """
    induced = induced_drag_coefficient(
        lift_coefficient, aspect_ratio, oswald_efficiency=oswald_efficiency
    )
    structural_penalty = structural_penalty_coefficient * aspect_ratio**2
    return parasitic_drag_coefficient + induced + structural_penalty


def optimize_aspect_ratio(
    lift_coefficient: float,
    parasitic_drag_coefficient: float,
    *,
    oswald_efficiency: float = 0.85,
    structural_penalty_coefficient: float = 1e-4,
    bounds: tuple[float, float] = (2.0, 40.0),
) -> OptimizationResult:
    """Find the aspect ratio minimizing induced drag plus structural penalty.

    Parameters
    ----------
    lift_coefficient:
        Wing lift coefficient.
    parasitic_drag_coefficient:
        Parasitic drag coefficient (does not affect the optimum's
        location, only the objective's value, since it's constant in AR).
    oswald_efficiency:
        Span efficiency factor, in ``(0, 1]``.
    structural_penalty_coefficient:
        Structural-weight penalty coefficient ``k``, > 0.
    bounds:
        Search bounds for the aspect ratio, ``(lower, upper)``.

    Returns
    -------
    OptimizationResult
        ``x`` is the optimal aspect ratio.

    Example
    -------
    The optimum has a closed form for this simplified objective,
    ``AR_opt = (CL^2 / (2*k*pi*e))^(1/3)`` -- used here as an independent
    check on the numerical optimizer:

    >>> result = optimize_aspect_ratio(lift_coefficient=0.5, parasitic_drag_coefficient=0.02)
    >>> round(result.x, 2)
    7.76

    """
    if structural_penalty_coefficient <= 0:
        raise OptimizationError(
            "structural_penalty_coefficient must be positive, got "
            f"{structural_penalty_coefficient!r}"
        )

    def objective(aspect_ratio: float) -> float:
        return total_drag_with_structural_penalty(
            aspect_ratio,
            lift_coefficient,
            parasitic_drag_coefficient,
            oswald_efficiency=oswald_efficiency,
            structural_penalty_coefficient=structural_penalty_coefficient,
        )

    return minimize_scalar_bounded(objective, bounds=bounds)
