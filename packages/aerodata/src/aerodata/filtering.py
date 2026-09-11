"""Time-series filtering and resampling for flight-test/telemetry data.

Reference
---------
- Moving-average (rolling-mean) smoothing and linear resampling to a
  uniform time base are standard first steps in flight-test data
  reduction, before any frequency-domain or model-fitting analysis
  (e.g. Klein & Morelli, *Aircraft System Identification: Theory and
  Practice*, AIAA, Ch. 2, on data preprocessing for flight test).

Assumptions
-----------
- ``moving_average`` uses a simple trailing rolling mean (pandas'
  default) -- not a more sophisticated filter (Butterworth, Kalman)
  that would better preserve phase or reject specific frequency bands;
  use it for basic noise smoothing only.
- ``resample_to_uniform_time`` uses linear interpolation between
  samples, which assumes the underlying signal is reasonably smooth
  between the original sample points -- it will not recover
  information lost to under-sampling or introduce anti-aliasing
  filtering.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from aerodata.exceptions import InvalidFlightDataError


def moving_average(series: pd.Series, window: int) -> pd.Series:
    """Compute a trailing moving-average (rolling-mean) smoothed series.

    Parameters
    ----------
    series:
        Input time series.
    window:
        Number of samples in the rolling window, > 0.

    Returns
    -------
    pandas.Series
        Smoothed series, same index as ``series``. The first
        ``window - 1`` entries are ``NaN`` (insufficient samples for a
        full window), matching pandas' standard rolling-window convention.

    Example
    -------
    >>> import pandas as pd
    >>> s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    >>> moving_average(s, window=3).tolist()
    [nan, nan, 2.0, 3.0, 4.0]

    """
    if window <= 0:
        raise InvalidFlightDataError(f"window must be positive, got {window!r}")
    if window > len(series):
        raise InvalidFlightDataError(
            f"window ({window}) must not exceed the series length ({len(series)})"
        )
    return series.rolling(window=window).mean()


def resample_to_uniform_time(df: pd.DataFrame, time_column: str, dt: float) -> pd.DataFrame:
    """Resample a DataFrame to a uniform time base via linear interpolation.

    Parameters
    ----------
    df:
        Input DataFrame, containing a time column and one or more
        numeric data columns.
    time_column:
        Name of the time column, must be present in ``df`` and sorted
        (strictly increasing).
    dt:
        Uniform time step for the resampled output, > 0, in the same
        units as ``time_column``.

    Returns
    -------
    pandas.DataFrame
        A new DataFrame with a uniformly-spaced time column and each
        other numeric column linearly interpolated onto that grid.

    Example
    -------
    >>> import pandas as pd
    >>> df = pd.DataFrame({"t": [0.0, 1.0, 2.0], "altitude": [100.0, 110.0, 130.0]})
    >>> resampled = resample_to_uniform_time(df, "t", dt=0.5)
    >>> resampled["altitude"].tolist()
    [100.0, 105.0, 110.0, 120.0, 130.0]

    """
    if time_column not in df.columns:
        raise InvalidFlightDataError(f"time_column {time_column!r} not found in DataFrame")
    if dt <= 0:
        raise InvalidFlightDataError(f"dt must be positive, got {dt!r}")
    times = df[time_column].to_numpy()
    if not np.all(np.diff(times) > 0):
        raise InvalidFlightDataError(f"{time_column!r} must be strictly increasing")

    new_times = np.arange(times[0], times[-1] + dt / 2, dt)
    new_times = new_times[new_times <= times[-1] + 1e-9]

    result = {time_column: new_times}
    for column in df.columns:
        if column == time_column:
            continue
        if pd.api.types.is_numeric_dtype(df[column]):
            result[column] = np.interp(new_times, times, df[column].to_numpy())
    return pd.DataFrame(result)
