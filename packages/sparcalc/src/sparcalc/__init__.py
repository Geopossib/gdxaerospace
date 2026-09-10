"""sparcalc — wing spar beam deflection and shear-flow analysis for GDX Aerospace."""

from __future__ import annotations

from sparcalc.beam import (
    cantilever_tip_deflection_distributed_load,
    cantilever_tip_deflection_point_load,
    cantilever_tip_slope_point_load,
    shear_flow,
)
from sparcalc.exceptions import InvalidSparInputError

__all__ = [
    "InvalidSparInputError",
    "cantilever_tip_deflection_distributed_load",
    "cantilever_tip_deflection_point_load",
    "cantilever_tip_slope_point_load",
    "shear_flow",
]

__version__ = "0.1.0"
