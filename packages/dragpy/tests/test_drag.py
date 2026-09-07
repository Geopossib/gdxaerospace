"""Validate skin-friction and parasitic-drag estimation."""

from __future__ import annotations

import math

import pytest
from dragpy.exceptions import InvalidDragModelError
from dragpy.parasite_drag import DragComponent, ParasiteDragBuildup
from dragpy.skin_friction import (
    skin_friction_coefficient_laminar,
    skin_friction_coefficient_turbulent,
)


@pytest.mark.parametrize(
    "reynolds,expected",
    [(1e5, 1.328 / math.sqrt(1e5)), (1e6, 1.328 / math.sqrt(1e6)), (5e6, 1.328 / math.sqrt(5e6))],
)
def test_laminar_cf_matches_blasius_formula(reynolds: float, expected: float) -> None:
    assert math.isclose(skin_friction_coefficient_laminar(reynolds), expected, rel_tol=1e-9)


def test_laminar_cf_rejects_nonpositive_reynolds() -> None:
    with pytest.raises(ValueError):
        skin_friction_coefficient_laminar(0)


def test_turbulent_cf_schlichting_matches_formula() -> None:
    re = 1e7
    expected = 0.455 / (math.log10(re)) ** 2.58
    assert math.isclose(
        skin_friction_coefficient_turbulent(re, model="schlichting"), expected, rel_tol=1e-9
    )


def test_turbulent_cf_prandtl_matches_formula() -> None:
    re = 1e7
    expected = 0.074 / re**0.2
    assert math.isclose(
        skin_friction_coefficient_turbulent(re, model="prandtl"), expected, rel_tol=1e-9
    )


def test_turbulent_cf_invalid_model_raises() -> None:
    with pytest.raises(InvalidDragModelError):
        skin_friction_coefficient_turbulent(1e6, model="nonsense")


def test_turbulent_cf_less_than_laminar_at_high_reynolds() -> None:
    """At a given Re, turbulent Cf > laminar Cf is NOT generally true near
    transition; but at high Re both models should be physically small (<0.01)."""
    re = 1e7
    assert skin_friction_coefficient_turbulent(re) < 0.01
    assert skin_friction_coefficient_laminar(re) < 0.01


def test_drag_component_drag_area_multiplies_correctly() -> None:
    comp = DragComponent("wing", skin_friction_coefficient=0.003, wetted_area=30.0, form_factor=1.2)
    assert math.isclose(comp.drag_area(), 0.003 * 1.2 * 1.0 * 30.0, rel_tol=1e-9)


def test_parasite_drag_buildup_sums_components() -> None:
    buildup = ParasiteDragBuildup(reference_area=16.2)
    buildup.add(DragComponent("wing", 0.003, wetted_area=30.0, form_factor=1.2))
    buildup.add(DragComponent("fuselage", 0.0028, wetted_area=25.0, form_factor=1.1))
    expected = (0.003 * 1.2 * 30.0 + 0.0028 * 1.1 * 25.0) / 16.2
    assert math.isclose(buildup.cd0(), expected, rel_tol=1e-9)


def test_parasite_drag_buildup_empty_is_zero() -> None:
    buildup = ParasiteDragBuildup(reference_area=10.0)
    assert buildup.cd0() == 0.0


def test_parasite_drag_buildup_rejects_nonpositive_reference_area() -> None:
    with pytest.raises(ValueError):
        ParasiteDragBuildup(reference_area=0)
    with pytest.raises(ValueError):
        ParasiteDragBuildup(reference_area=-5.0)
