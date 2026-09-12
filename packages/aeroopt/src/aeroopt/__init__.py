"""aeroopt — a SciPy optimization wrapper and worked aerospace examples."""

from __future__ import annotations

from aeroopt.exceptions import OptimizationError
from aeroopt.optimize import OptimizationResult, minimize_scalar_bounded, minimize_with_bounds
from aeroopt.wing_design import optimize_aspect_ratio, total_drag_with_structural_penalty

__all__ = [
    "OptimizationError",
    "OptimizationResult",
    "minimize_scalar_bounded",
    "minimize_with_bounds",
    "optimize_aspect_ratio",
    "total_drag_with_structural_penalty",
]

__version__ = "0.1.0"
