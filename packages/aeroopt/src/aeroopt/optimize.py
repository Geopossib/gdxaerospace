"""A thin, ergonomic wrapper around SciPy's constrained/bounded optimizers.

Reference
---------
- Virtanen, P. et al., "SciPy 1.0: Fundamental Algorithms for
  Scientific Computing in Python", Nature Methods, 2020 -- the
  underlying ``scipy.optimize`` routines this module wraps
  (``minimize_scalar`` with ``method="bounded"`` for 1D problems,
  ``minimize`` with ``method="SLSQP"`` for constrained multivariate
  problems).

Assumptions
-----------
- This module does not implement any new optimization algorithm; it
  standardizes SciPy's various result-object shapes into one
  :class:`OptimizationResult` and adds basic input validation with
  GDX Aerospace's own exception type, matching the "wrap, don't
  reinvent" approach used elsewhere in the ecosystem (e.g. ``satprop``
  wrapping ``sgp4``).
- Gradient-free by default (SciPy estimates derivatives numerically
  unless the objective function itself returns them) -- adequate for
  the smooth, low-dimensional conceptual-design problems this module
  targets, not a substitute for analytic-gradient large-scale
  optimization.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np
from scipy.optimize import minimize as scipy_minimize
from scipy.optimize import minimize_scalar

from aeroopt.exceptions import OptimizationError


@dataclass(frozen=True)
class OptimizationResult:
    """A standardized optimization result, regardless of which SciPy routine ran it."""

    x: float | np.ndarray
    """The optimal point found: a float for 1D problems, an array for multivariate."""
    fun: float
    """Objective function value at ``x``."""
    success: bool
    """Whether the solver reports convergence."""
    message: str
    """Solver status message."""
    n_iterations: int
    """Number of iterations the solver took."""


def minimize_scalar_bounded(
    objective: Callable[[float], float], bounds: tuple[float, float]
) -> OptimizationResult:
    """Minimize a scalar (1D) objective function over a bounded interval.

    Parameters
    ----------
    objective:
        A function taking one float and returning one float.
    bounds:
        ``(lower, upper)`` bounds to search within, with ``lower < upper``.

    Returns
    -------
    OptimizationResult

    Example
    -------
    >>> result = minimize_scalar_bounded(lambda x: (x - 3.0) ** 2, bounds=(0.0, 10.0))
    >>> round(result.x, 4)
    3.0
    >>> result.success
    True

    """
    lower, upper = bounds
    if lower >= upper:
        raise OptimizationError(f"bounds must satisfy lower < upper, got {bounds!r}")

    result = minimize_scalar(objective, bounds=bounds, method="bounded")
    return OptimizationResult(
        x=float(result.x),
        fun=float(result.fun),
        success=bool(result.success),
        message=str(result.message),
        n_iterations=int(result.nit),
    )


def minimize_with_bounds(
    objective: Callable[[np.ndarray], float],
    x0: Sequence[float],
    *,
    bounds: Sequence[tuple[float, float]] | None = None,
    constraints: Sequence[dict] | None = None,
    method: str = "SLSQP",
) -> OptimizationResult:
    """Minimize a multivariate objective function, optionally with bounds/constraints.

    Parameters
    ----------
    objective:
        A function taking a 1D array and returning a scalar.
    x0:
        Initial guess, shape ``(n,)``.
    bounds:
        Optional per-variable ``(lower, upper)`` bounds, length ``n``.
    constraints:
        Optional SciPy-style constraint dicts (see ``scipy.optimize.minimize``
        documentation for the expected format).
    method:
        SciPy optimizer name. Defaults to ``"SLSQP"``, which supports
        both bounds and general constraints.

    Returns
    -------
    OptimizationResult

    Example
    -------
    Minimize ``(x-1)^2 + (y-2)^2``, unconstrained:

    >>> result = minimize_with_bounds(
    ...     lambda v: (v[0] - 1.0) ** 2 + (v[1] - 2.0) ** 2, x0=[0.0, 0.0]
    ... )
    >>> [round(float(v), 4) for v in result.x]
    [1.0, 2.0]

    """
    if len(x0) == 0:
        raise OptimizationError("x0 must not be empty")

    result = scipy_minimize(
        objective,
        x0=np.asarray(x0, dtype=float),
        bounds=bounds,
        constraints=constraints,
        method=method,
    )
    n_iterations = int(getattr(result, "nit", 0))
    return OptimizationResult(
        x=np.asarray(result.x, dtype=float),
        fun=float(result.fun),
        success=bool(result.success),
        message=str(result.message),
        n_iterations=n_iterations,
    )
