"""Validate cross-section geometric property calculations."""

from __future__ import annotations

import math

import pytest
from aerostruct.exceptions import InvalidSectionError
from aerostruct.sections import (
    circle_properties,
    hollow_circle_properties,
    i_beam_properties,
    parallel_axis_theorem,
    rectangle_properties,
)


def test_parallel_axis_theorem_matches_formula() -> None:
    i_c, area, d = 1e-6, 0.001, 0.05
    expected = i_c + area * d**2
    assert math.isclose(parallel_axis_theorem(i_c, area, d), expected, rel_tol=1e-9)


def test_parallel_axis_theorem_zero_distance_unchanged() -> None:
    assert math.isclose(parallel_axis_theorem(1e-6, 0.001, 0.0), 1e-6, rel_tol=1e-9)


def test_parallel_axis_theorem_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidSectionError):
        parallel_axis_theorem(-1e-6, 0.001, 0.05)
    with pytest.raises(InvalidSectionError):
        parallel_axis_theorem(1e-6, 0, 0.05)


def test_rectangle_properties_matches_formula() -> None:
    w, h = 0.02, 0.1
    props = rectangle_properties(w, h)
    assert math.isclose(props.area, w * h, rel_tol=1e-9)
    assert math.isclose(props.ixx, w * h**3 / 12, rel_tol=1e-9)
    assert math.isclose(props.iyy, h * w**3 / 12, rel_tol=1e-9)


def test_rectangle_taller_has_larger_ixx() -> None:
    """A taller (same-width) rectangle resists bending about x better -- larger Ixx."""
    short = rectangle_properties(width=0.02, height=0.05)
    tall = rectangle_properties(width=0.02, height=0.1)
    assert tall.ixx > short.ixx
    assert math.isclose(tall.area, 2 * short.area, rel_tol=1e-9)


def test_rectangle_properties_rejects_nonpositive_dimensions() -> None:
    with pytest.raises(InvalidSectionError):
        rectangle_properties(0, 0.1)
    with pytest.raises(InvalidSectionError):
        rectangle_properties(0.1, -1.0)


def test_circle_properties_matches_formula() -> None:
    r = 0.05
    props = circle_properties(r)
    assert props.j is not None
    assert math.isclose(props.area, math.pi * r**2, rel_tol=1e-9)
    assert math.isclose(props.ixx, math.pi * r**4 / 4, rel_tol=1e-9)
    assert math.isclose(props.iyy, props.ixx, rel_tol=1e-9)
    assert math.isclose(props.j, math.pi * r**4 / 2, rel_tol=1e-9)


def test_circle_j_equals_two_times_i() -> None:
    """Polar moment J = Ixx + Iyy = 2*I for a circle (by symmetry)."""
    props = circle_properties(0.05)
    assert props.j is not None
    assert math.isclose(props.j, 2 * props.ixx, rel_tol=1e-9)


def test_circle_properties_rejects_nonpositive_radius() -> None:
    with pytest.raises(InvalidSectionError):
        circle_properties(0)


def test_hollow_circle_reduces_to_solid_as_inner_radius_shrinks() -> None:
    solid = circle_properties(0.05)
    nearly_hollow = hollow_circle_properties(0.05, 1e-9)
    assert math.isclose(nearly_hollow.area, solid.area, rel_tol=1e-6)
    assert math.isclose(nearly_hollow.ixx, solid.ixx, rel_tol=1e-6)


def test_hollow_circle_less_area_than_solid_same_outer_radius() -> None:
    solid = circle_properties(0.05)
    hollow = hollow_circle_properties(0.05, 0.04)
    assert hollow.area < solid.area
    assert hollow.ixx < solid.ixx


def test_hollow_circle_rejects_invalid_radii() -> None:
    with pytest.raises(InvalidSectionError):
        hollow_circle_properties(0.04, 0.05)  # outer < inner
    with pytest.raises(InvalidSectionError):
        hollow_circle_properties(0.05, -0.01)


def test_i_beam_properties_matches_composite_hand_calculation() -> None:
    fw, ft, hw, tw = 0.08, 0.01, 0.1, 0.006
    props = i_beam_properties(fw, ft, hw, tw)

    flange_area = fw * ft
    web_area = tw * hw
    expected_area = 2 * flange_area + web_area
    assert math.isclose(props.area, expected_area, rel_tol=1e-9)

    flange_ixx_own = fw * ft**3 / 12
    d = hw / 2 + ft / 2
    flange_ixx_shifted = flange_ixx_own + flange_area * d**2
    web_ixx = tw * hw**3 / 12
    expected_ixx = 2 * flange_ixx_shifted + web_ixx
    assert math.isclose(props.ixx, expected_ixx, rel_tol=1e-9)


def test_i_beam_ixx_much_larger_than_solid_rectangle_same_area() -> None:
    """The whole point of an I-beam: much more bending stiffness for the same
    material, by moving area away from the neutral axis."""
    i_beam = i_beam_properties(
        flange_width=0.08, flange_thickness=0.01, web_height=0.1, web_thickness=0.006
    )
    equivalent_rect_height = i_beam.area / 0.08
    equivalent_rect = rectangle_properties(width=0.08, height=equivalent_rect_height)
    assert i_beam.ixx > equivalent_rect.ixx


def test_i_beam_properties_rejects_nonpositive_dimensions() -> None:
    with pytest.raises(InvalidSectionError):
        i_beam_properties(0, 0.01, 0.1, 0.006)
    with pytest.raises(InvalidSectionError):
        i_beam_properties(0.08, 0.01, 0.1, -0.006)
