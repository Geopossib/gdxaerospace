"""Validate Basquin S-N fatigue life and Miner's-rule cumulative damage."""

from __future__ import annotations

import math

import pytest
from fatiguepy.exceptions import InvalidFatigueInputError
from fatiguepy.sn_curve import basquin_life, basquin_stress_amplitude, miners_rule_damage


def test_basquin_life_matches_formula() -> None:
    sigma_a, a, b = 300e6, 1000e6, -0.1
    expected = (sigma_a / a) ** (1 / b)
    assert math.isclose(basquin_life(sigma_a, a, b), expected, rel_tol=1e-9)


def test_basquin_life_and_stress_amplitude_are_inverses() -> None:
    a, b = 1000e6, -0.1
    n = basquin_life(300e6, a, b)
    recovered_stress = basquin_stress_amplitude(n, a, b)
    assert math.isclose(recovered_stress, 300e6, rel_tol=1e-6)


def test_basquin_life_higher_stress_gives_shorter_life() -> None:
    a, b = 1000e6, -0.1
    life_low_stress = basquin_life(200e6, a, b)
    life_high_stress = basquin_life(400e6, a, b)
    assert life_high_stress < life_low_stress


def test_basquin_life_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidFatigueInputError):
        basquin_life(0, 1000e6, -0.1)
    with pytest.raises(InvalidFatigueInputError):
        basquin_life(300e6, 0, -0.1)
    with pytest.raises(InvalidFatigueInputError):
        basquin_life(300e6, 1000e6, 0.1)  # exponent must be negative


def test_basquin_stress_amplitude_matches_formula() -> None:
    n, a, b = 100000.0, 1000e6, -0.1
    expected = a * n**b
    assert math.isclose(basquin_stress_amplitude(n, a, b), expected, rel_tol=1e-9)


def test_basquin_stress_amplitude_rejects_invalid_inputs() -> None:
    with pytest.raises(InvalidFatigueInputError):
        basquin_stress_amplitude(0, 1000e6, -0.1)
    with pytest.raises(InvalidFatigueInputError):
        basquin_stress_amplitude(100000.0, 1000e6, 0.0)


def test_miners_rule_damage_matches_formula() -> None:
    applied = [1000.0, 2000.0]
    to_failure = [10000.0, 8000.0]
    expected = sum(n / big_n for n, big_n in zip(applied, to_failure, strict=True))
    assert math.isclose(miners_rule_damage(applied, to_failure), expected, rel_tol=1e-9)


def test_miners_rule_damage_full_life_at_one_level_gives_unity() -> None:
    """Applying exactly N_f cycles at a single stress level gives damage = 1.0."""
    damage = miners_rule_damage([10000.0], [10000.0])
    assert math.isclose(damage, 1.0, rel_tol=1e-9)


def test_miners_rule_damage_zero_cycles_gives_zero_damage() -> None:
    assert miners_rule_damage([0.0, 0.0], [10000.0, 8000.0]) == 0.0


def test_miners_rule_damage_predicts_failure_above_unity() -> None:
    damage = miners_rule_damage([8000.0, 6000.0], [10000.0, 8000.0])
    assert damage > 1.0  # 0.8 + 0.75 = 1.55 -> predicted failure


def test_miners_rule_damage_rejects_mismatched_lengths() -> None:
    with pytest.raises(InvalidFatigueInputError):
        miners_rule_damage([1000.0, 2000.0], [10000.0])


def test_miners_rule_damage_rejects_empty_input() -> None:
    with pytest.raises(InvalidFatigueInputError):
        miners_rule_damage([], [])


def test_miners_rule_damage_rejects_negative_cycles_applied() -> None:
    with pytest.raises(InvalidFatigueInputError):
        miners_rule_damage([-100.0], [10000.0])


def test_miners_rule_damage_rejects_nonpositive_cycles_to_failure() -> None:
    with pytest.raises(InvalidFatigueInputError):
        miners_rule_damage([1000.0], [0.0])
