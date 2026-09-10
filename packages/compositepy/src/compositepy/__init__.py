"""compositepy — orthotropic lamina stiffness, transformation, and failure criteria."""

from __future__ import annotations

from compositepy.exceptions import InvalidLaminaError
from compositepy.failure import LaminaStrengths, max_stress_margins, tsai_hill_failure_index
from compositepy.lamina import (
    ReducedStiffness,
    TransformedStiffness,
    reduced_stiffness,
    transform_stiffness,
)

__all__ = [
    "InvalidLaminaError",
    "LaminaStrengths",
    "ReducedStiffness",
    "TransformedStiffness",
    "max_stress_margins",
    "reduced_stiffness",
    "transform_stiffness",
    "tsai_hill_failure_index",
]

__version__ = "0.1.0"
