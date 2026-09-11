"""aerodata — aerospace-aware flight-test/telemetry time-series analysis."""

from __future__ import annotations

from aerodata.analysis import DescriptiveStats, descriptive_stats, detect_outliers_zscore
from aerodata.columns import STANDARD_COLUMNS
from aerodata.exceptions import InvalidFlightDataError
from aerodata.filtering import moving_average, resample_to_uniform_time

__all__ = [
    "STANDARD_COLUMNS",
    "DescriptiveStats",
    "InvalidFlightDataError",
    "descriptive_stats",
    "detect_outliers_zscore",
    "moving_average",
    "resample_to_uniform_time",
]

__version__ = "0.1.0"
