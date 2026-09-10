"""Validate fundamental stress, strain, and failure-theory calculations."""

from __future__ import annotations

import math

import pytest
from stresspy.exceptions import InvalidStressInputError
from stresspy.stress import (
    axial_stress,
    bending_stress,
    principal_stresses,
    torsional_shear_stress,
    transverse_shear_stress,
    von_mises_stress,
)


def test_axial_stress_matches_formula() -> None:
    assert math.isclose(axial_stress(50_000.0, 0.001), 50_000.0 / 0.001, rel_tol=1e-9)


def test_axial_stress_negative_force_gives_compressive_stress() -> None:
    assert axial_stress(-50_000.0, 0.001) < 0


def test_axial_stress_rejects_nonpositive_area() -> None:
    with pytest.raises(InvalidStressInputError):
        axial_stress(1000.0, 0)


def test_bending_stress_matches_formula() -> None:
    m, c, i = 5000.0, 0.05, 1.667e-6
    assert math.isclose(bending_stress(m, c, i), m * c / i, rel_tol=1e-9)


def test_bending_stress_zero_at_neutral_axis() -> None:
    assert bending_stress(5000.0, 0.0, 1.667e-6) == 0.0


def test_bending_stress_scales_linearly_with_distance() -> None:
    m, i = 5000.0, 1.667e-6
    near = bending_stress(m, 0.02, i)
    far = bending_stress(m, 0.04, i)
    assert math.isclose(far, 2 * near, rel_tol=1e-9)


def test_bending_stress_rejects_nonpositive_moment_of_inertia() -> None:
    with pytest.raises(InvalidStressInputError):
        bending_stress(5000.0, 0.05, 0)


def test_transverse_shear_stress_matches_formula() -> None:
    v, q, i, t = 1000.0, 2e-5, 1.667e-6, 0.02
    assert math.isclose(transverse_shear_stress(v, q, i, t), v * q / (i * t), rel_tol=1e-9)


def test_transverse_shear_stress_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidStressInputError):
        transverse_shear_stress(1000.0, 2e-5, 0, 0.02)
    with pytest.raises(InvalidStressInputError):
        transverse_shear_stress(1000.0, 2e-5, 1.667e-6, 0)


def test_torsional_shear_stress_matches_formula() -> None:
    t, r, j = 200.0, 0.02, 9.817e-6
    assert math.isclose(torsional_shear_stress(t, r, j), t * r / j, rel_tol=1e-9)


def test_torsional_shear_stress_zero_at_center() -> None:
    assert torsional_shear_stress(200.0, 0.0, 9.817e-6) == 0.0


def test_torsional_shear_stress_rejects_nonpositive_j() -> None:
    with pytest.raises(InvalidStressInputError):
        torsional_shear_stress(200.0, 0.02, 0)


def test_von_mises_pure_uniaxial_equals_the_stress_itself() -> None:
    """For pure uniaxial tension (sigma_y=0, tau_xy=0), von Mises reduces to |sigma_x|."""
    assert math.isclose(von_mises_stress(150e6, 0.0, 0.0), 150e6, rel_tol=1e-9)


def test_von_mises_matches_formula() -> None:
    sx, sy, txy = 150e6, 0.0, 50e6
    expected = math.sqrt(sx**2 - sx * sy + sy**2 + 3 * txy**2)
    assert math.isclose(von_mises_stress(sx, sy, txy), expected, rel_tol=1e-9)


def test_von_mises_pure_shear_matches_known_factor() -> None:
    """For pure shear (sigma_x=sigma_y=0), von Mises = sqrt(3)*tau."""
    tau = 50e6
    assert math.isclose(von_mises_stress(0.0, 0.0, tau), math.sqrt(3) * tau, rel_tol=1e-9)


def test_von_mises_is_nonnegative() -> None:
    assert von_mises_stress(-100e6, 50e6, -30e6) >= 0


def test_principal_stresses_sum_equals_sigma_x_plus_sigma_y() -> None:
    """Stress invariant: sigma_1 + sigma_2 = sigma_x + sigma_y (trace is invariant)."""
    sx, sy, txy = 100e6, 40e6, 30e6
    result = principal_stresses(sx, sy, txy)
    assert math.isclose(result.sigma_1 + result.sigma_2, sx + sy, rel_tol=1e-9)


def test_principal_stresses_sigma_1_exceeds_sigma_2() -> None:
    result = principal_stresses(100e6, 40e6, 30e6)
    assert result.sigma_1 > result.sigma_2


def test_principal_stresses_pure_uniaxial_no_shear() -> None:
    """With sigma_y=0 and tau_xy=0, principal stresses are just sigma_x and 0."""
    result = principal_stresses(100e6, 0.0, 0.0)
    assert math.isclose(result.sigma_1, 100e6, rel_tol=1e-9)
    assert math.isclose(result.sigma_2, 0.0, abs_tol=1e-6)
    assert math.isclose(result.tau_max, 50e6, rel_tol=1e-9)


def test_principal_stresses_zero_shear_when_already_principal() -> None:
    """If sigma_x == sigma_y and tau_xy == 0, the state is already isotropic
    (hydrostatic in-plane); tau_max should be zero."""
    result = principal_stresses(50e6, 50e6, 0.0)
    assert math.isclose(result.tau_max, 0.0, abs_tol=1e-6)
