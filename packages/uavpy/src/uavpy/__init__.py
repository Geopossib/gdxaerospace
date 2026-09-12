"""uavpy — UAV sizing and performance estimation for GDX Aerospace."""

from __future__ import annotations

from uavpy.exceptions import InvalidUAVInputError
from uavpy.fixed_wing import stall_speed, thrust_to_weight_ratio, wing_loading
from uavpy.multirotor import G0, Multirotor, actual_hover_power, ideal_hover_power

__all__ = [
    "G0",
    "InvalidUAVInputError",
    "Multirotor",
    "actual_hover_power",
    "ideal_hover_power",
    "stall_speed",
    "thrust_to_weight_ratio",
    "wing_loading",
]

__version__ = "0.1.0"
