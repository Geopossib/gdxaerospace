"""Validate proportional-navigation and waypoint guidance relations."""

from __future__ import annotations

import math

import numpy as np
import pytest
from guidancepy.exceptions import InvalidGuidanceInputError
from guidancepy.proportional_navigation import (
    closing_velocity,
    line_of_sight_rate,
    proportional_navigation_command,
    zero_effort_miss_time_to_go,
)
from guidancepy.waypoint import cross_track_error, distance_to_waypoint, waypoint_bearing


def test_los_rate_matches_formula() -> None:
    p, v = np.array([1000.0, 0.0]), np.array([-200.0, 50.0])
    expected = (p[0] * v[1] - p[1] * v[0]) / (p[0] ** 2 + p[1] ** 2)
    assert math.isclose(line_of_sight_rate(p, v), expected, rel_tol=1e-9)


def test_los_rate_zero_on_direct_collision_course() -> None:
    """If relative velocity points directly along the LOS (pure closing), LOS rate is zero."""
    p = np.array([1000.0, 500.0])
    v = -p / np.linalg.norm(p) * 300.0  # velocity purely along -p (closing directly)
    assert math.isclose(line_of_sight_rate(p, v), 0.0, abs_tol=1e-9)


def test_los_rate_rejects_zero_relative_position() -> None:
    with pytest.raises(InvalidGuidanceInputError):
        line_of_sight_rate(np.zeros(2), np.array([1.0, 0.0]))


def test_los_rate_rejects_bad_shape() -> None:
    with pytest.raises(InvalidGuidanceInputError):
        line_of_sight_rate(np.array([1.0, 0.0, 0.0]), np.array([1.0, 0.0]))


def test_closing_velocity_matches_formula() -> None:
    p, v = np.array([1000.0, 0.0]), np.array([-200.0, 50.0])
    expected = -(p @ v) / np.linalg.norm(p)
    assert math.isclose(closing_velocity(p, v), expected, rel_tol=1e-9)


def test_closing_velocity_positive_when_approaching() -> None:
    p = np.array([1000.0, 0.0])
    v = np.array([-300.0, 0.0])  # moving directly toward interceptor
    assert closing_velocity(p, v) > 0


def test_closing_velocity_negative_when_receding() -> None:
    p = np.array([1000.0, 0.0])
    v = np.array([300.0, 0.0])  # moving directly away
    assert closing_velocity(p, v) < 0


def test_closing_velocity_rejects_zero_relative_position() -> None:
    with pytest.raises(InvalidGuidanceInputError):
        closing_velocity(np.zeros(2), np.array([1.0, 0.0]))


def test_pn_command_matches_formula() -> None:
    vc, los_rate, n = 200.0, 0.05, 4.0
    assert math.isclose(
        proportional_navigation_command(vc, los_rate, navigation_constant=n),
        n * vc * los_rate,
        rel_tol=1e-9,
    )


def test_pn_command_zero_when_los_rate_zero() -> None:
    """On a direct collision course (LOS rate = 0), PN commands zero lateral acceleration."""
    assert proportional_navigation_command(200.0, 0.0) == 0.0


def test_pn_command_scales_with_navigation_constant() -> None:
    low = proportional_navigation_command(200.0, 0.05, navigation_constant=3.0)
    high = proportional_navigation_command(200.0, 0.05, navigation_constant=6.0)
    assert math.isclose(high, 2 * low, rel_tol=1e-9)


def test_time_to_go_matches_formula() -> None:
    assert math.isclose(zero_effort_miss_time_to_go(1000.0, 200.0), 5.0, rel_tol=1e-9)


def test_time_to_go_rejects_nonpositive_inputs() -> None:
    with pytest.raises(InvalidGuidanceInputError):
        zero_effort_miss_time_to_go(0, 200.0)
    with pytest.raises(InvalidGuidanceInputError):
        zero_effort_miss_time_to_go(1000.0, 0)


def test_waypoint_bearing_cardinal_directions() -> None:
    origin = np.array([0.0, 0.0])
    assert math.isclose(waypoint_bearing(origin, np.array([1.0, 0.0])), 0.0, abs_tol=1e-9)
    assert math.isclose(
        waypoint_bearing(origin, np.array([0.0, 1.0])), math.pi / 2, abs_tol=1e-9
    )
    assert math.isclose(
        waypoint_bearing(origin, np.array([-1.0, 0.0])), math.pi, abs_tol=1e-9
    )


def test_waypoint_bearing_rejects_coincident_points() -> None:
    p = np.array([5.0, 5.0])
    with pytest.raises(InvalidGuidanceInputError):
        waypoint_bearing(p, p)


def test_distance_to_waypoint_matches_euclidean_distance() -> None:
    assert math.isclose(
        distance_to_waypoint(np.array([0.0, 0.0]), np.array([3.0, 4.0])), 5.0, rel_tol=1e-9
    )


def test_distance_to_waypoint_zero_at_same_point() -> None:
    p = np.array([10.0, 20.0])
    assert distance_to_waypoint(p, p) == 0.0


def test_cross_track_error_zero_on_path() -> None:
    on_path = np.array([50.0, 0.0])
    assert math.isclose(
        cross_track_error(on_path, np.array([0.0, 0.0]), np.array([100.0, 0.0])),
        0.0,
        abs_tol=1e-9,
    )


def test_cross_track_error_sign_convention() -> None:
    """Positive cross-track error is to the left of the path direction."""
    left_of_path = np.array([50.0, 10.0])
    right_of_path = np.array([50.0, -10.0])
    cte_left = cross_track_error(left_of_path, np.array([0.0, 0.0]), np.array([100.0, 0.0]))
    cte_right = cross_track_error(right_of_path, np.array([0.0, 0.0]), np.array([100.0, 0.0]))
    assert cte_left > 0
    assert cte_right < 0
    assert math.isclose(cte_left, -cte_right, rel_tol=1e-9)


def test_cross_track_error_rejects_degenerate_path() -> None:
    p = np.array([1.0, 1.0])
    with pytest.raises(InvalidGuidanceInputError):
        cross_track_error(np.array([5.0, 5.0]), p, p)
