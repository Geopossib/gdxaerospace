"""rocketperf — rocket engine performance relations for GDX Aerospace."""

from __future__ import annotations

from rocketperf.exceptions import InvalidRocketInputError
from rocketperf.performance import (
    G0,
    characteristic_velocity,
    effective_exhaust_velocity,
    ideal_delta_v,
    mass_ratio_for_delta_v,
    specific_impulse_rocket,
    thrust_coefficient,
)

__all__ = [
    "G0",
    "InvalidRocketInputError",
    "characteristic_velocity",
    "effective_exhaust_velocity",
    "ideal_delta_v",
    "mass_ratio_for_delta_v",
    "specific_impulse_rocket",
    "thrust_coefficient",
]

__version__ = "0.1.0"
