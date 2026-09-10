"""Validate the material property database lookup and structure."""

from __future__ import annotations

import math

import pytest
from aeromaterials.database import available_materials, get_material
from aeromaterials.exceptions import UnknownMaterialError


def test_get_material_returns_correct_name() -> None:
    material = get_material("Al7075-T6")
    assert material.name == "Al7075-T6"


def test_get_material_al7075_t6_values() -> None:
    material = get_material("Al7075-T6")
    assert math.isclose(material.density, 2810.0)
    assert math.isclose(material.youngs_modulus, 71.7e9)
    assert math.isclose(material.yield_strength, 503e6)
    assert math.isclose(material.ultimate_strength, 572e6)


def test_get_material_unknown_raises() -> None:
    with pytest.raises(UnknownMaterialError):
        get_material("Unobtainium-42")


def test_get_material_unknown_error_lists_available_materials() -> None:
    with pytest.raises(UnknownMaterialError, match="Al7075-T6"):
        get_material("nonexistent")


def test_available_materials_includes_known_entries() -> None:
    names = available_materials()
    assert "Al7075-T6" in names
    assert "Al2024-T3" in names
    assert "Ti-6Al-4V" in names


def test_available_materials_is_sorted() -> None:
    names = available_materials()
    assert list(names) == sorted(names)


def test_every_material_has_positive_density_and_modulus() -> None:
    for name in available_materials():
        material = get_material(name)
        assert material.density > 0
        assert material.youngs_modulus > 0
        assert material.shear_modulus > 0
        assert 0 < material.poisson_ratio < 0.5


def test_every_material_has_a_nonempty_source() -> None:
    for name in available_materials():
        material = get_material(name)
        assert len(material.source) > 0


def test_ultimate_strength_exceeds_yield_where_both_given() -> None:
    """Ultimate tensile strength should always be >= yield strength."""
    for name in available_materials():
        material = get_material(name)
        if material.yield_strength is not None and material.ultimate_strength is not None:
            assert material.ultimate_strength >= material.yield_strength


def test_titanium_is_less_dense_than_steel_but_denser_than_aluminum() -> None:
    ti = get_material("Ti-6Al-4V")
    al = get_material("Al7075-T6")
    steel = get_material("ASTM-A36-steel")
    assert al.density < ti.density < steel.density
