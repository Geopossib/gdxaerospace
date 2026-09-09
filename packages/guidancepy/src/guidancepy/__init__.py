"""guidancepy — proportional navigation and waypoint guidance for GDX Aerospace."""

from __future__ import annotations

from guidancepy.exceptions import InvalidGuidanceInputError
from guidancepy.proportional_navigation import (
    closing_velocity,
    line_of_sight_rate,
    proportional_navigation_command,
    zero_effort_miss_time_to_go,
)
from guidancepy.waypoint import cross_track_error, distance_to_waypoint, waypoint_bearing

__all__ = [
    "InvalidGuidanceInputError",
    "closing_velocity",
    "cross_track_error",
    "distance_to_waypoint",
    "line_of_sight_rate",
    "proportional_navigation_command",
    "waypoint_bearing",
    "zero_effort_miss_time_to_go",
]

__version__ = "0.1.0"
