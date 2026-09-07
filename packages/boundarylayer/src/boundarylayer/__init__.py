"""boundarylayer — laminar/turbulent flat-plate boundary-layer relations."""

from __future__ import annotations

from boundarylayer.exceptions import InvalidReynoldsNumberError
from boundarylayer.thickness import (
    laminar_local_skin_friction,
    laminar_thickness,
    turbulent_local_skin_friction,
    turbulent_thickness,
)

__all__ = [
    "InvalidReynoldsNumberError",
    "laminar_local_skin_friction",
    "laminar_thickness",
    "turbulent_local_skin_friction",
    "turbulent_thickness",
]

__version__ = "0.1.0"
