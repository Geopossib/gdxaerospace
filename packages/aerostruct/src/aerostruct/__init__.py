"""aerostruct — cross-section geometric properties for GDX Aerospace."""

from __future__ import annotations

from aerostruct.exceptions import InvalidSectionError
from aerostruct.sections import (
    SectionProperties,
    circle_properties,
    hollow_circle_properties,
    i_beam_properties,
    parallel_axis_theorem,
    rectangle_properties,
)

__all__ = [
    "InvalidSectionError",
    "SectionProperties",
    "circle_properties",
    "hollow_circle_properties",
    "i_beam_properties",
    "parallel_axis_theorem",
    "rectangle_properties",
]

__version__ = "0.1.0"
