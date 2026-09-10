"""Validate the SGP4 wrapper and two-body propagation."""

from __future__ import annotations

import datetime as dt
import math

import numpy as np
import pytest
from satprop.exceptions import PropagationError
from satprop.sgp4_wrapper import propagate_tle
from satprop.two_body import two_body_propagate

from orbitpy import circular_velocity, orbital_period

_LINE1 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
_LINE2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
_EPOCH = dt.datetime(2008, 9, 20, 12, 25, 40)


def test_propagate_tle_at_epoch_gives_iss_scale_orbit() -> None:
    position, velocity = propagate_tle(_LINE1, _LINE2, _EPOCH)
    r = float(np.linalg.norm(position))
    v = float(np.linalg.norm(velocity))
    assert 6_600_000 < r < 6_900_000  # ISS orbital radius range
    assert 7500 < v < 7800  # ISS orbital speed range


def test_propagate_tle_returns_si_units() -> None:
    """Position magnitude should be on the order of 1e6-1e7 m, not 1e3-1e4 km."""
    position, _ = propagate_tle(_LINE1, _LINE2, _EPOCH)
    assert float(np.linalg.norm(position)) > 1e6


def test_propagate_tle_position_changes_over_time() -> None:
    pos1, _ = propagate_tle(_LINE1, _LINE2, _EPOCH)
    pos2, _ = propagate_tle(_LINE1, _LINE2, _EPOCH + dt.timedelta(minutes=10))
    assert not np.allclose(pos1, pos2)


def test_propagate_tle_returns_to_similar_position_after_one_period() -> None:
    """Propagating forward by exactly one orbital period (from the TLE's own mean
    motion) should return close to the starting position."""
    mean_motion_rev_per_day = 15.72125391
    period_minutes = 1440.0 / mean_motion_rev_per_day
    pos1, _ = propagate_tle(_LINE1, _LINE2, _EPOCH)
    pos2, _ = propagate_tle(_LINE1, _LINE2, _EPOCH + dt.timedelta(minutes=period_minutes))
    separation = float(np.linalg.norm(pos1 - pos2))
    assert separation < 50_000  # within 50 km after one rev (J2 nodal/apsidal drift, etc.)


def test_propagate_tle_raises_on_garbage_input() -> None:
    with pytest.raises(Exception):  # noqa: B017 - sgp4/our wrapper may raise various types
        propagate_tle("not a valid tle line", "also not valid", _EPOCH)


def test_two_body_propagate_full_period_returns_to_start() -> None:
    r0 = np.array([7_000_000.0, 0.0, 0.0])
    v0 = np.array([0.0, circular_velocity(7_000_000.0), 0.0])
    period = orbital_period(7_000_000.0)
    r1, v1 = two_body_propagate(r0, v0, period)
    assert np.allclose(r0, r1, atol=1.0)
    assert np.allclose(v0, v1, atol=1e-3)


def test_two_body_propagate_half_period_reaches_opposite_side() -> None:
    r0 = np.array([7_000_000.0, 0.0, 0.0])
    v0 = np.array([0.0, circular_velocity(7_000_000.0), 0.0])
    period = orbital_period(7_000_000.0)
    r1, _ = two_body_propagate(r0, v0, period / 2)
    assert np.allclose(r1, -r0, atol=10.0)


def test_two_body_propagate_forward_then_backward_returns_to_start() -> None:
    r0 = np.array([7_000_000.0, 0.0, 0.0])
    v0 = np.array([0.0, circular_velocity(7_000_000.0), 0.0])
    period = orbital_period(7_000_000.0)
    fwd_r, fwd_v = two_body_propagate(r0, v0, period / 4)
    back_r, back_v = two_body_propagate(fwd_r, fwd_v, -period / 4)
    assert np.allclose(back_r, r0, atol=1.0)
    assert np.allclose(back_v, v0, atol=1e-3)


def test_two_body_propagate_zero_time_returns_same_state() -> None:
    r0 = np.array([7_000_000.0, 0.0, 0.0])
    v0 = np.array([0.0, circular_velocity(7_000_000.0), 0.0])
    r1, v1 = two_body_propagate(r0, v0, 0.0)
    assert np.allclose(r0, r1, atol=1.0)
    assert np.allclose(v0, v1, atol=1e-3)


def test_two_body_propagate_conserves_energy() -> None:
    """Specific orbital energy should be conserved under pure two-body propagation."""
    from orbitpy.constants import EARTH_MU

    r0 = np.array([7_500_000.0, 500_000.0, 200_000.0])
    v0 = np.array([-1000.0, 7200.0, 500.0])
    energy0 = float(v0 @ v0) / 2 - EARTH_MU / float(np.linalg.norm(r0))

    r1, v1 = two_body_propagate(r0, v0, 3000.0)
    energy1 = float(v1 @ v1) / 2 - EARTH_MU / float(np.linalg.norm(r1))
    assert math.isclose(energy0, energy1, rel_tol=1e-6)


def test_two_body_propagate_rejects_hyperbolic_state() -> None:
    r0 = np.array([7_000_000.0, 0.0, 0.0])
    v0 = np.array([0.0, 20000.0, 0.0])  # far exceeds escape velocity
    with pytest.raises(PropagationError):
        two_body_propagate(r0, v0, 100.0)
