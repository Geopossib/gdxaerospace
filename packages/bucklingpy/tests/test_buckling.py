"""Validate Euler column and flat-plate buckling calculations."""

from __future__ import annotations

import math

import pytest
from bucklingpy.buckling import (
    K_FIXED_FIXED,
    K_FIXED_FREE,
    K_FIXED_PINNED,
    K_PINNED_PINNED,
    InvalidBucklingInputError,
    euler_buckling_load,
    euler_buckling_stress,
    plate_buckling_stress,
)


def test_euler_buckling_load_matches_formula() -> None:
    e, i, length = 71.7e9, 1e-6, 2.0
    expected = math.pi**2 * e * i / length**2
    assert math.isclose(euler_buckling_load(e, i, length), expected, rel_tol=1e-9)


def test_euler_buckling_load_fixed_free_is_quarter_of_pinned_pinned() -> None:
    """Fixed-free (K=2) buckling load is 1/4 that of pinned-pinned (K=1) for the
    same length -- the classic textbook comparison of end-condition efficiency."""
    e, i, length = 71.7e9, 1e-6, 2.0
    pinned = euler_buckling_load(e, i, length, k_factor=K_PINNED_PINNED)
    fixed_free = euler_buckling_load(e, i, length, k_factor=K_FIXED_FREE)
    assert math.isclose(fixed_free, pinned / 4, rel_tol=1e-9)


def test_euler_buckling_load_fixed_fixed_is_four_times_pinned_pinned() -> None:
    e, i, length = 71.7e9, 1e-6, 2.0
    pinned = euler_buckling_load(e, i, length, k_factor=K_PINNED_PINNED)
    fixed_fixed = euler_buckling_load(e, i, length, k_factor=K_FIXED_FIXED)
    assert math.isclose(fixed_fixed, pinned * 4, rel_tol=1e-9)


def test_euler_buckling_load_ordering_of_end_conditions() -> None:
    """Stiffer end conditions (smaller K) give higher buckling load, for fixed
    E, I, length: fixed-fixed > fixed-pinned > pinned-pinned > fixed-free."""
    e, i, length = 71.7e9, 1e-6, 2.0
    fixed_fixed = euler_buckling_load(e, i, length, k_factor=K_FIXED_FIXED)
    fixed_pinned = euler_buckling_load(e, i, length, k_factor=K_FIXED_PINNED)
    pinned_pinned = euler_buckling_load(e, i, length, k_factor=K_PINNED_PINNED)
    fixed_free = euler_buckling_load(e, i, length, k_factor=K_FIXED_FREE)
    assert fixed_fixed > fixed_pinned > pinned_pinned > fixed_free


def test_euler_buckling_load_inversely_proportional_to_length_squared() -> None:
    e, i = 71.7e9, 1e-6
    short = euler_buckling_load(e, i, 1.0)
    long_ = euler_buckling_load(e, i, 2.0)
    assert math.isclose(short / long_, 4.0, rel_tol=1e-9)  # 2^2 = 4


def test_euler_buckling_load_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidBucklingInputError):
        euler_buckling_load(0, 1e-6, 2.0)
    with pytest.raises(InvalidBucklingInputError):
        euler_buckling_load(71.7e9, 0, 2.0)
    with pytest.raises(InvalidBucklingInputError):
        euler_buckling_load(71.7e9, 1e-6, 0)
    with pytest.raises(InvalidBucklingInputError):
        euler_buckling_load(71.7e9, 1e-6, 2.0, k_factor=0)


def test_euler_buckling_stress_matches_formula() -> None:
    e, r, length = 71.7e9, 0.01, 2.0
    expected = math.pi**2 * e / (length / r) ** 2
    assert math.isclose(euler_buckling_stress(e, r, length), expected, rel_tol=1e-9)


def test_euler_buckling_stress_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidBucklingInputError):
        euler_buckling_stress(71.7e9, 0, 2.0)


def test_plate_buckling_stress_matches_formula() -> None:
    e, nu, t, b = 71.7e9, 0.33, 0.002, 0.1
    expected = 4.0 * math.pi**2 * e / (12 * (1 - nu**2)) * (t / b) ** 2
    assert math.isclose(plate_buckling_stress(e, nu, t, b), expected, rel_tol=1e-9)


def test_plate_buckling_stress_increases_with_thickness_squared() -> None:
    e, nu, b = 71.7e9, 0.33, 0.1
    thin = plate_buckling_stress(e, nu, thickness=0.001, width=b)
    thick = plate_buckling_stress(e, nu, thickness=0.002, width=b)
    assert math.isclose(thick / thin, 4.0, rel_tol=1e-9)  # (2t/t)^2 = 4


def test_plate_buckling_stress_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidBucklingInputError):
        plate_buckling_stress(71.7e9, 0.6, 0.002, 0.1)  # poisson out of range
    with pytest.raises(InvalidBucklingInputError):
        plate_buckling_stress(71.7e9, 0.33, 0, 0.1)
    with pytest.raises(InvalidBucklingInputError):
        plate_buckling_stress(71.7e9, 0.33, 0.002, 0)
