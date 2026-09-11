"""Descriptive statistics and z-score outlier detection for flight-test/telemetry data.

Reference
---------
- The z-score outlier screen (flagging points more than a threshold
  number of standard deviations from the mean) is a standard,
  general-purpose first pass for flight-test data quality checks,
  distinct from -- but conceptually similar to -- the anomaly-detection
  approach in ``sattelemetry.archive`` for decoded telemetry channels.

Assumptions
-----------
- The z-score method assumes an approximately Gaussian distribution for
  the series; it is a general-purpose first screen, not a substitute
  for a channel-specific anomaly model. As with any z-score approach, a
  single extreme outlier in a short series can inflate its own standard
  deviation enough to partially mask itself -- most reliable over a
  reasonably long, mostly-nominal series.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from aerodata.exceptions import InvalidFlightDataError


@dataclass(frozen=True)
class DescriptiveStats:
    """Basic descriptive statistics for a data series."""

    mean: float
    std: float
    minimum: float
    maximum: float
    median: float


def descriptive_stats(series: pd.Series) -> DescriptiveStats:
    """Compute basic descriptive statistics for a data series.

    Parameters
    ----------
    series:
        Input data series, must contain at least one non-null value.

    Returns
    -------
    DescriptiveStats

    Example
    -------
    >>> import pandas as pd
    >>> s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    >>> stats = descriptive_stats(s)
    >>> stats.mean, stats.std, stats.minimum, stats.maximum, stats.median
    (3.0, 1.5811388300841898, 1.0, 5.0, 3.0)

    """
    clean = series.dropna()
    if len(clean) == 0:
        raise InvalidFlightDataError("series contains no non-null values")
    return DescriptiveStats(
        mean=float(clean.mean()),
        std=float(clean.std()),
        minimum=float(clean.min()),
        maximum=float(clean.max()),
        median=float(clean.median()),
    )


def detect_outliers_zscore(series: pd.Series, *, threshold: float = 3.0) -> pd.Series:
    """Flag statistically outlying points in a series via a z-score screen.

    A point is flagged when its value is more than ``threshold``
    standard deviations from the series mean.

    Parameters
    ----------
    series:
        Input data series.
    threshold:
        Number of standard deviations from the mean to flag, > 0.
        Defaults to 3.0.

    Returns
    -------
    pandas.Series
        Boolean mask, same index as ``series``, True where a point is
        flagged as an outlier. Returns an all-False mask if the series
        has fewer than 2 non-null values or zero variance (nothing can
        be an outlier in a constant series).

    Example
    -------
    >>> import pandas as pd
    >>> s = pd.Series([10.0, 10.1, 9.9, 10.0, 9.8, 10.2, 9.9, 10.1, 9.8, 10.0, 50.0])
    >>> mask = detect_outliers_zscore(s)
    >>> s[mask].tolist()
    [50.0]

    """
    if threshold <= 0:
        raise InvalidFlightDataError(f"threshold must be positive, got {threshold!r}")
    mean = series.mean()
    std = series.std()
    if len(series.dropna()) < 2 or std == 0 or pd.isna(std):
        return pd.Series(False, index=series.index)
    z_scores = (series - mean).abs() / std
    return z_scores > threshold
