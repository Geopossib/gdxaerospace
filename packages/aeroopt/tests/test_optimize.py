"""Validate the SciPy optimization wrapper."""

from __future__ import annotations

import math

import numpy as np
import pytest
from aeroopt.exceptions import OptimizationError
from aeroopt.optimize import minimize_scalar_bounded, minimize_with_bounds


def test_minimize_scalar_bounded_finds_known_minimum() -> None:
    result = minimize_scalar_bounded(lambda x: (x - 3.0) ** 2, bounds=(0.0, 10.0))
    assert math.isclose(result.x, 3.0, abs_tol=1e-4)
    assert result.success


def test_minimize_scalar_bounded_respects_bounds() -> None:
    """If the unconstrained minimum is outside the bounds, the result should sit
    at (or very near) the boundary closest to the true minimum."""
    result = minimize_scalar_bounded(lambda x: (x - 20.0) ** 2, bounds=(0.0, 10.0))
    assert math.isclose(result.x, 10.0, abs_tol=1e-3)


def test_minimize_scalar_bounded_rejects_invalid_bounds() -> None:
    with pytest.raises(OptimizationError):
        minimize_scalar_bounded(lambda x: x**2, bounds=(5.0, 2.0))
    with pytest.raises(OptimizationError):
        minimize_scalar_bounded(lambda x: x**2, bounds=(5.0, 5.0))


def test_minimize_scalar_bounded_fun_matches_objective_at_x() -> None:
    def objective(x: float) -> float:
        return (x - 3.0) ** 2

    result = minimize_scalar_bounded(objective, bounds=(0.0, 10.0))
    x = result.x
    assert isinstance(x, float)
    assert math.isclose(result.fun, objective(x), rel_tol=1e-6)


def test_minimize_with_bounds_finds_known_minimum() -> None:
    result = minimize_with_bounds(
        lambda v: (v[0] - 1.0) ** 2 + (v[1] - 2.0) ** 2, x0=[0.0, 0.0]
    )
    assert np.allclose(result.x, [1.0, 2.0], atol=1e-4)
    assert result.success


def test_minimize_with_bounds_respects_variable_bounds() -> None:
    result = minimize_with_bounds(lambda v: (v[0] - 5.0) ** 2, x0=[0.0], bounds=[(0.0, 2.0)])
    x = result.x
    assert isinstance(x, np.ndarray)
    assert math.isclose(x[0], 2.0, abs_tol=1e-3)


def test_minimize_with_bounds_respects_constraint() -> None:
    """Minimize x+y subject to x+y >= 1 (tight at the constraint boundary)."""
    constraints = [{"type": "ineq", "fun": lambda v: v[0] + v[1] - 1.0}]
    result = minimize_with_bounds(lambda v: v[0] + v[1], x0=[1.0, 1.0], constraints=constraints)
    x = result.x
    assert isinstance(x, np.ndarray)
    assert math.isclose(x[0] + x[1], 1.0, abs_tol=1e-3)


def test_minimize_with_bounds_rejects_empty_x0() -> None:
    with pytest.raises(OptimizationError):
        minimize_with_bounds(lambda v: 0.0, x0=[])


def test_minimize_with_bounds_fun_matches_objective_at_x() -> None:
    def objective(v: np.ndarray) -> float:
        return float((v[0] - 1.0) ** 2 + (v[1] - 2.0) ** 2)

    result = minimize_with_bounds(objective, x0=[0.0, 0.0])
    x = result.x
    assert isinstance(x, np.ndarray)
    assert math.isclose(result.fun, objective(x), rel_tol=1e-6)
