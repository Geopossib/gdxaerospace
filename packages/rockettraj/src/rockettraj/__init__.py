"""rockettraj — vertical rocket trajectory simulation for GDX Aerospace."""

from __future__ import annotations

from rockettraj.exceptions import InvalidTrajectoryInputError
from rockettraj.trajectory import G0, RocketConfig, TrajectoryResult, simulate_trajectory

__all__ = [
    "G0",
    "InvalidTrajectoryInputError",
    "RocketConfig",
    "TrajectoryResult",
    "simulate_trajectory",
]

__version__ = "0.1.0"
