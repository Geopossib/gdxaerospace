"""Validate lamina failure criteria (max stress, Tsai-Hill)."""

from __future__ import annotations

import math

import pytest
from compositepy.exceptions import InvalidLaminaError
from compositepy.failure import LaminaStrengths, max_stress_margins, tsai_hill_failure_index

_STRENGTHS = LaminaStrengths(
    x_tension=1500e6, x_compression=1500e6, y_tension=40e6, y_compression=246e6, s=68e6
)


def test_lamina_strengths_rejects_nonpositive_values() -> None:
    with pytest.raises(InvalidLaminaError):
        LaminaStrengths(
            x_tension=0, x_compression=1500e6, y_tension=40e6, y_compression=246e6, s=68e6
        )


def test_max_stress_margins_matches_formula() -> None:
    sigma_1, sigma_2, tau_12 = 200e6, 10e6, 20e6
    margins = max_stress_margins(sigma_1, sigma_2, tau_12, _STRENGTHS)
    assert math.isclose(margins["fiber"], 1500e6 / 200e6 - 1, rel_tol=1e-9)
    assert math.isclose(margins["transverse"], 40e6 / 10e6 - 1, rel_tol=1e-9)
    assert math.isclose(margins["shear"], 68e6 / 20e6 - 1, rel_tol=1e-9)


def test_max_stress_margins_governing_is_minimum() -> None:
    margins = max_stress_margins(200e6, 10e6, 20e6, _STRENGTHS)
    assert margins["governing"] == min(
        margins["fiber"], margins["transverse"], margins["shear"]
    )


def test_max_stress_margins_uses_compression_strength_for_negative_stress() -> None:
    margins_tension = max_stress_margins(200e6, 10e6, 0.0, _STRENGTHS)
    margins_compression = max_stress_margins(-200e6, -10e6, 0.0, _STRENGTHS)
    # Same magnitude, but y_compression (246e6) >> y_tension (40e6), so the
    # compression case should show a much larger transverse margin.
    assert margins_compression["transverse"] > margins_tension["transverse"]


def test_max_stress_margins_predicts_failure_when_stress_exceeds_strength() -> None:
    margins = max_stress_margins(sigma_1=1600e6, sigma_2=0.0, tau_12=0.0, strengths=_STRENGTHS)
    assert margins["fiber"] < 0


def test_max_stress_margins_zero_stress_gives_infinite_margin() -> None:
    margins = max_stress_margins(0.0, 0.0, 0.0, _STRENGTHS)
    assert margins["fiber"] == math.inf
    assert margins["transverse"] == math.inf
    assert margins["shear"] == math.inf


def test_tsai_hill_matches_formula() -> None:
    sigma_1, sigma_2, tau_12 = 200e6, 10e6, 20e6
    x, y, s = _STRENGTHS.x_tension, _STRENGTHS.y_tension, _STRENGTHS.s
    expected = (
        (sigma_1 / x) ** 2 - (sigma_1 * sigma_2) / x**2 + (sigma_2 / y) ** 2 + (tau_12 / s) ** 2
    )
    assert math.isclose(
        tsai_hill_failure_index(sigma_1, sigma_2, tau_12, _STRENGTHS), expected, rel_tol=1e-9
    )


def test_tsai_hill_zero_stress_gives_zero_index() -> None:
    assert tsai_hill_failure_index(0.0, 0.0, 0.0, _STRENGTHS) == 0.0


def test_tsai_hill_predicts_failure_at_ultimate_uniaxial_stress() -> None:
    """At sigma_1 = X (fiber strength) with no other stress, FI should equal 1
    exactly (this degenerates to the max-stress fiber mode)."""
    fi = tsai_hill_failure_index(_STRENGTHS.x_tension, 0.0, 0.0, _STRENGTHS)
    assert math.isclose(fi, 1.0, rel_tol=1e-9)


def test_tsai_hill_below_one_for_safe_state() -> None:
    fi = tsai_hill_failure_index(200e6, 10e6, 20e6, _STRENGTHS)
    assert 0 < fi < 1
