"""Validate the minimum-drag aspect-ratio worked optimization example."""

from __future__ import annotations

import math

import pytest
from aeroopt.exceptions import OptimizationError
from aeroopt.wing_design import optimize_aspect_ratio, total_drag_with_structural_penalty
from wingtools.finite_wing import induced_drag_coefficient


def test_total_drag_matches_formula() -> None:
    ar, cl, cd0, e, k = 8.0, 0.5, 0.02, 0.85, 1e-4
    expected = cd0 + induced_drag_coefficient(cl, ar, oswald_efficiency=e) + k * ar**2
    assert math.isclose(
        total_drag_with_structural_penalty(
            ar, cl, cd0, oswald_efficiency=e, structural_penalty_coefficient=k
        ),
        expected,
        rel_tol=1e-9,
    )


def test_total_drag_decreases_then_increases_with_aspect_ratio() -> None:
    """The combined objective should have an interior minimum: induced drag falls
    with AR while the structural penalty grows, so cost falls then rises."""
    low_ar = total_drag_with_structural_penalty(3.0, 0.5, 0.02)
    mid_ar = total_drag_with_structural_penalty(8.0, 0.5, 0.02)
    high_ar = total_drag_with_structural_penalty(30.0, 0.5, 0.02)
    assert mid_ar < low_ar
    assert mid_ar < high_ar


def test_optimize_aspect_ratio_matches_closed_form_solution() -> None:
    """This simplified objective has a closed-form optimum:
    AR_opt = (CL^2/(2*k*pi*e))^(1/3) -- an independent check on the numerical result."""
    cl, k, e = 0.5, 1e-4, 0.85
    result = optimize_aspect_ratio(
        lift_coefficient=cl,
        parasitic_drag_coefficient=0.02,
        oswald_efficiency=e,
        structural_penalty_coefficient=k,
    )
    closed_form_ar = (cl**2 / (2 * k * math.pi * e)) ** (1 / 3)
    assert math.isclose(result.x, closed_form_ar, rel_tol=1e-3)


def test_optimize_aspect_ratio_is_a_local_minimum() -> None:
    """The optimum should give a lower cost than nearby points on both sides."""
    result = optimize_aspect_ratio(lift_coefficient=0.5, parasitic_drag_coefficient=0.02)
    cost_at_optimum = result.fun
    cost_slightly_lower = total_drag_with_structural_penalty(result.x - 0.5, 0.5, 0.02)
    cost_slightly_higher = total_drag_with_structural_penalty(result.x + 0.5, 0.5, 0.02)
    assert cost_at_optimum <= cost_slightly_lower
    assert cost_at_optimum <= cost_slightly_higher


def test_optimize_aspect_ratio_higher_penalty_gives_lower_optimal_ar() -> None:
    """A stiffer structural penalty should push the optimum toward a lower aspect ratio."""
    low_penalty = optimize_aspect_ratio(
        lift_coefficient=0.5, parasitic_drag_coefficient=0.02, structural_penalty_coefficient=1e-5
    )
    high_penalty = optimize_aspect_ratio(
        lift_coefficient=0.5, parasitic_drag_coefficient=0.02, structural_penalty_coefficient=1e-3
    )
    assert high_penalty.x < low_penalty.x


def test_optimize_aspect_ratio_rejects_nonpositive_penalty() -> None:
    with pytest.raises(OptimizationError):
        optimize_aspect_ratio(
            lift_coefficient=0.5,
            parasitic_drag_coefficient=0.02,
            structural_penalty_coefficient=0,
        )
