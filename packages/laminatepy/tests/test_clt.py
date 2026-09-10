"""Validate classical laminate theory ABD matrix assembly and laminate response."""

from __future__ import annotations

import math

import numpy as np
import pytest
from compositepy.lamina import reduced_stiffness, transform_stiffness
from laminatepy.clt import Ply, compute_abd, laminate_response
from laminatepy.exceptions import InvalidLaminateError

_Q = reduced_stiffness(e1=181e9, e2=10.3e9, nu12=0.28, g12=7.17e9)  # T300/5208


def test_single_ply_a_matrix_matches_q_bar_times_thickness() -> None:
    thickness = 0.001
    abd = compute_abd([Ply(thickness, 0.0, _Q)])
    assert math.isclose(abd.a[0, 0], _Q.q11 * thickness, rel_tol=1e-9)
    assert math.isclose(abd.a[1, 1], _Q.q22 * thickness, rel_tol=1e-9)
    assert math.isclose(abd.a[0, 1], _Q.q12 * thickness, rel_tol=1e-9)


def test_single_ply_b_matrix_is_zero() -> None:
    """A single ply is trivially symmetric about its own mid-plane: B = 0 exactly."""
    abd = compute_abd([Ply(0.001, 0.0, _Q)])
    assert np.allclose(abd.b, 0.0, atol=1e-15)


def test_single_ply_d_matrix_matches_formula() -> None:
    thickness = 0.001
    abd = compute_abd([Ply(thickness, 0.0, _Q)])
    assert math.isclose(abd.d[0, 0], _Q.q11 * thickness**3 / 12, rel_tol=1e-9)


def test_symmetric_laminate_has_zero_b_matrix() -> None:
    """The core CLT identity this module's correctness hinges on: any laminate
    that is mirror-symmetric about its mid-plane has B = 0 exactly."""
    plies = [
        Ply(0.001, 0.0, _Q),
        Ply(0.001, math.radians(90), _Q),
        Ply(0.001, math.radians(90), _Q),
        Ply(0.001, 0.0, _Q),
    ]
    abd = compute_abd(plies)
    assert np.allclose(abd.b, 0.0, atol=1e-9)


def test_symmetric_laminate_with_mixed_angles_still_has_zero_b() -> None:
    plies = [
        Ply(0.001, math.radians(45), _Q),
        Ply(0.001, math.radians(-45), _Q),
        Ply(0.001, 0.0, _Q),
        Ply(0.001, 0.0, _Q),
        Ply(0.001, math.radians(-45), _Q),
        Ply(0.001, math.radians(45), _Q),
    ]
    abd = compute_abd(plies)
    assert np.allclose(abd.b, 0.0, atol=1e-9)


def test_asymmetric_laminate_has_nonzero_b() -> None:
    """A [0/90] two-ply stack is not mirror-symmetric about its mid-plane, so
    (unlike the symmetric cases above) B should come out nonzero."""
    plies = [Ply(0.001, 0.0, _Q), Ply(0.001, math.radians(90), _Q)]
    abd = compute_abd(plies)
    assert not np.allclose(abd.b, 0.0, atol=1e-6)


def test_compute_abd_matrices_are_symmetric() -> None:
    """A, B, D must each be symmetric matrices (a property of the underlying
    transformed stiffness matrix, which is itself symmetric)."""
    plies = [Ply(0.001, math.radians(30), _Q), Ply(0.0015, math.radians(-15), _Q)]
    abd = compute_abd(plies)
    assert np.allclose(abd.a, abd.a.T)
    assert np.allclose(abd.b, abd.b.T)
    assert np.allclose(abd.d, abd.d.T)


def test_compute_abd_a_matrix_additive_over_plies() -> None:
    """For plies of equal thickness and the same angle, A should scale linearly
    with the number of plies (since each contributes Q_bar * thickness equally)."""
    one_ply = compute_abd([Ply(0.001, 0.0, _Q)])
    three_plies = compute_abd([Ply(0.001, 0.0, _Q) for _ in range(3)])
    assert np.allclose(three_plies.a, 3 * one_ply.a, rtol=1e-9)


def test_compute_abd_rejects_empty_ply_list() -> None:
    with pytest.raises(InvalidLaminateError):
        compute_abd([])


def test_ply_rejects_nonpositive_thickness() -> None:
    with pytest.raises(InvalidLaminateError):
        Ply(0, 0.0, _Q)
    with pytest.raises(InvalidLaminateError):
        Ply(-0.001, 0.0, _Q)


def test_laminate_response_recovers_applied_load() -> None:
    """Solving for strain/curvature, then multiplying back through ABD, should
    reproduce the originally applied load (round-trip through the linear system)."""
    plies = [Ply(0.001, math.radians(0), _Q), Ply(0.001, math.radians(90), _Q)]
    abd = compute_abd(plies)
    n_applied = np.array([1e5, 2e4, 5e3])
    m_applied = np.array([10.0, -5.0, 2.0])
    eps0, kappa = laminate_response(abd, n_applied, m_applied)

    full_matrix = np.block([[abd.a, abd.b], [abd.b, abd.d]])
    recovered_loads = full_matrix @ np.concatenate([eps0, kappa])
    assert np.allclose(recovered_loads, np.concatenate([n_applied, m_applied]), rtol=1e-6)


def test_laminate_response_zero_load_gives_zero_response() -> None:
    abd = compute_abd([Ply(0.001, 0.0, _Q)])
    eps0, kappa = laminate_response(abd, np.zeros(3), np.zeros(3))
    assert np.allclose(eps0, 0.0)
    assert np.allclose(kappa, 0.0)


def test_laminate_response_symmetric_laminate_decouples_membrane_and_bending() -> None:
    """For a symmetric laminate (B=0), applying only an in-plane load should
    produce zero curvature (no membrane-bending coupling)."""
    plies = [Ply(0.001, 0.0, _Q), Ply(0.001, math.radians(90), _Q), Ply(0.001, 0.0, _Q)]
    abd = compute_abd(plies)
    eps0, kappa = laminate_response(abd, np.array([1e5, 0.0, 0.0]), np.zeros(3))
    assert np.allclose(kappa, 0.0, atol=1e-9)
    assert eps0[0] != 0.0


def test_laminate_response_rejects_bad_shapes() -> None:
    abd = compute_abd([Ply(0.001, 0.0, _Q)])
    with pytest.raises(InvalidLaminateError):
        laminate_response(abd, np.array([1.0, 2.0]), np.zeros(3))


def test_q_bar_used_in_abd_matches_compositepy_directly() -> None:
    """Sanity check that laminatepy's internal Q_bar assembly matches calling
    compositepy.transform_stiffness directly."""
    angle = math.radians(30)
    abd = compute_abd([Ply(0.002, angle, _Q)])
    q_bar = transform_stiffness(_Q, angle)
    assert math.isclose(abd.a[0, 0], q_bar.q11 * 0.002, rel_tol=1e-9)
