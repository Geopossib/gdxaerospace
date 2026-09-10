"""satprop — TLE (sgp4) and two-body satellite propagation for GDX Aerospace."""

from __future__ import annotations

from satprop.exceptions import PropagationError
from satprop.sgp4_wrapper import propagate_tle
from satprop.two_body import two_body_propagate

__all__ = [
    "PropagationError",
    "propagate_tle",
    "two_body_propagate",
]

__version__ = "0.1.0"
