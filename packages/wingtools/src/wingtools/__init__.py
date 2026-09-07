"""wingtools — finite-wing lift and induced-drag corrections for GDX Aerospace."""

from __future__ import annotations

from wingtools.exceptions import InvalidWingGeometryError
from wingtools.finite_wing import (
    finite_wing_lift_curve_slope,
    induced_drag_coefficient,
    oswald_efficiency_estimate,
)

__all__ = [
    "InvalidWingGeometryError",
    "finite_wing_lift_curve_slope",
    "induced_drag_coefficient",
    "oswald_efficiency_estimate",
]

__version__ = "0.1.0"
