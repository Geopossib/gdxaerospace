"""autopilotpy — PID control and simple autopilot hold modes for GDX Aerospace."""

from __future__ import annotations

from autopilotpy.exceptions import InvalidControllerConfigError
from autopilotpy.hold_modes import AltitudeHoldAutopilot, HeadingHoldAutopilot, heading_error
from autopilotpy.pid import PIDController

__all__ = [
    "AltitudeHoldAutopilot",
    "HeadingHoldAutopilot",
    "InvalidControllerConfigError",
    "PIDController",
    "heading_error",
]

__version__ = "0.1.0"
