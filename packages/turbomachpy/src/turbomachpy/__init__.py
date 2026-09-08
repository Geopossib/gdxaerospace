"""turbomachpy — ideal-cycle compressor and turbine stage relations for GDX Aerospace."""

from __future__ import annotations

from turbomachpy.exceptions import InvalidTurbomachineryInputError
from turbomachpy.stage import compressor_temperature_rise, specific_work, turbine_temperature_drop

__all__ = [
    "InvalidTurbomachineryInputError",
    "compressor_temperature_rise",
    "specific_work",
    "turbine_temperature_drop",
]

__version__ = "0.1.0"
