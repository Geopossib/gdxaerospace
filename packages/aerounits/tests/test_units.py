"""Numerical validation tests for aerounits."""

from __future__ import annotations

import math

from aerounits import Q_, ureg


def test_knot_to_ms_conversion() -> None:
    """1 knot = 1852 m / 3600 s exactly, per the international nautical mile."""
    one_knot_in_ms = Q_(1, "knot").to("m/s").magnitude
    assert math.isclose(one_knot_in_ms, 1852 / 3600, rel_tol=1e-9)


def test_foot_to_meter_conversion() -> None:
    """1 ft = 0.3048 m exactly (international foot)."""
    assert math.isclose(Q_(1, "ft").to("m").magnitude, 0.3048, rel_tol=1e-9)


def test_slug_to_kilogram_conversion() -> None:
    """1 slug = 14.59390 kg (NIST reference value)."""
    assert math.isclose(
        Q_(1, "slug").to("kg").magnitude, 14.5939029372, rel_tol=1e-9
    )


def test_pressure_psi_to_pascal() -> None:
    """1 psi = 6894.757... Pa."""
    psi_in_pa = Q_(1, "psi").to("Pa").magnitude
    assert math.isclose(psi_in_pa, 6894.757293168361, rel_tol=1e-6)


def test_shared_registry_is_reused() -> None:
    """Two Q_ quantities must come from the same registry to be combinable."""
    a = Q_(1, "m")
    b = Q_(1, "ft")
    total = a + b  # would raise DimensionalityError across mismatched registries
    assert total._REGISTRY is ureg
