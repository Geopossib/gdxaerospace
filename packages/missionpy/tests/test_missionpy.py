"""Validate eclipse-fraction and delta-v-budget calculations."""

from __future__ import annotations

import math

import pytest
from missionpy.delta_v_budget import DeltaVBudget
from missionpy.eclipse import eclipse_duration, eclipse_fraction
from missionpy.exceptions import InvalidMissionInputError

from orbitpy import orbital_period


def test_eclipse_fraction_leo_in_plausible_range() -> None:
    """LEO eclipse fraction is commonly cited as roughly a third to 40% of the orbit."""
    f = eclipse_fraction(6_778_000.0)
    assert 0.3 < f < 0.45


def test_eclipse_fraction_decreases_with_altitude() -> None:
    """Higher orbits subtend a smaller shadow angle relative to the full orbit."""
    low = eclipse_fraction(6_778_000.0)
    high = eclipse_fraction(20_000_000.0)
    assert high < low


def test_eclipse_fraction_zero_at_high_beta_angle() -> None:
    """A sufficiently large beta angle means the orbit never enters the shadow cylinder."""
    f = eclipse_fraction(6_778_000.0, beta_angle=math.radians(89.9))
    assert f == 0.0


def test_eclipse_fraction_zero_at_edge_on_beta() -> None:
    f = eclipse_fraction(6_778_000.0, beta_angle=math.pi / 2)
    assert f == 0.0


def test_eclipse_fraction_maximum_at_zero_beta() -> None:
    f0 = eclipse_fraction(6_778_000.0, beta_angle=0.0)
    f30 = eclipse_fraction(6_778_000.0, beta_angle=math.radians(30))
    assert f0 > f30


def test_eclipse_fraction_rejects_orbit_inside_earth() -> None:
    with pytest.raises(InvalidMissionInputError):
        eclipse_fraction(5_000_000.0)  # below Earth's surface


def test_eclipse_fraction_rejects_invalid_beta_angle() -> None:
    with pytest.raises(InvalidMissionInputError):
        eclipse_fraction(6_778_000.0, beta_angle=-0.1)
    with pytest.raises(InvalidMissionInputError):
        eclipse_fraction(6_778_000.0, beta_angle=math.pi)


def test_eclipse_duration_matches_fraction_times_period() -> None:
    r = 6_778_000.0
    period = orbital_period(r)
    fraction = eclipse_fraction(r)
    duration = eclipse_duration(r, period)
    assert math.isclose(duration, fraction * period, rel_tol=1e-9)


def test_eclipse_duration_rejects_nonpositive_period() -> None:
    with pytest.raises(InvalidMissionInputError):
        eclipse_duration(6_778_000.0, 0)


# --- Delta-v budget ---


def test_delta_v_budget_subtotal_sums_items() -> None:
    budget = DeltaVBudget()
    budget.add("launch insertion", 100.0)
    budget.add("orbit raise", 3000.0)
    assert math.isclose(budget.subtotal(), 3100.0, rel_tol=1e-9)


def test_delta_v_budget_total_with_margin() -> None:
    budget = DeltaVBudget(margin_fraction=0.05)
    budget.add("a", 1000.0)
    budget.add("b", 500.0)
    assert math.isclose(budget.total_with_margin(), 1500.0 * 1.05, rel_tol=1e-9)


def test_delta_v_budget_zero_margin_by_default() -> None:
    budget = DeltaVBudget()
    budget.add("a", 1000.0)
    assert math.isclose(budget.total_with_margin(), budget.subtotal(), rel_tol=1e-9)


def test_delta_v_budget_overwrites_same_name() -> None:
    budget = DeltaVBudget()
    budget.add("maneuver", 100.0)
    budget.add("maneuver", 200.0)  # should overwrite, not add
    assert math.isclose(budget.subtotal(), 200.0, rel_tol=1e-9)


def test_delta_v_budget_items_returns_copy() -> None:
    budget = DeltaVBudget()
    budget.add("a", 100.0)
    items = budget.items()
    items["a"] = 999.0  # mutating the returned copy must not affect the budget
    assert math.isclose(budget.subtotal(), 100.0, rel_tol=1e-9)


def test_delta_v_budget_rejects_negative_margin() -> None:
    with pytest.raises(InvalidMissionInputError):
        DeltaVBudget(margin_fraction=-0.1)


def test_delta_v_budget_rejects_negative_delta_v() -> None:
    budget = DeltaVBudget()
    with pytest.raises(InvalidMissionInputError):
        budget.add("bad", -100.0)


def test_delta_v_budget_empty_is_zero() -> None:
    budget = DeltaVBudget()
    assert budget.subtotal() == 0.0
    assert budget.total_with_margin() == 0.0
