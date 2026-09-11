"""Validate moving-average filtering and uniform-time resampling."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest
from aerodata.exceptions import InvalidFlightDataError
from aerodata.filtering import moving_average, resample_to_uniform_time


def test_moving_average_matches_manual_computation() -> None:
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    result = moving_average(s, window=3)
    expected = [None, None, 2.0, 3.0, 4.0]
    for actual, exp in zip(result.tolist(), expected, strict=True):
        if exp is None:
            assert math.isnan(actual)
        else:
            assert math.isclose(actual, exp, rel_tol=1e-9)


def test_moving_average_window_one_returns_original_series() -> None:
    s = pd.Series([1.0, 5.0, 3.0])
    result = moving_average(s, window=1)
    assert result.tolist() == s.tolist()


def test_moving_average_full_window_gives_single_valid_value() -> None:
    s = pd.Series([1.0, 2.0, 3.0])
    result = moving_average(s, window=3)
    assert math.isnan(result.iloc[0])
    assert math.isnan(result.iloc[1])
    assert math.isclose(result.iloc[2], 2.0, rel_tol=1e-9)


def test_moving_average_rejects_nonpositive_window() -> None:
    s = pd.Series([1.0, 2.0, 3.0])
    with pytest.raises(InvalidFlightDataError):
        moving_average(s, window=0)
    with pytest.raises(InvalidFlightDataError):
        moving_average(s, window=-1)


def test_moving_average_rejects_window_larger_than_series() -> None:
    s = pd.Series([1.0, 2.0])
    with pytest.raises(InvalidFlightDataError):
        moving_average(s, window=5)


def test_resample_matches_linear_interpolation() -> None:
    df = pd.DataFrame({"t": [0.0, 1.0, 2.0], "altitude": [100.0, 110.0, 130.0]})
    result = resample_to_uniform_time(df, "t", dt=0.5)
    expected_altitude = np.interp(
        result["t"].to_numpy(), df["t"].to_numpy(), df["altitude"].to_numpy()
    )
    assert np.allclose(result["altitude"].to_numpy(), expected_altitude)


def test_resample_output_time_is_uniformly_spaced() -> None:
    df = pd.DataFrame({"t": [0.0, 1.3, 3.7], "value": [1.0, 2.0, 3.0]})
    result = resample_to_uniform_time(df, "t", dt=0.25)
    diffs = np.diff(result["t"].to_numpy())
    assert np.allclose(diffs, 0.25, atol=1e-9)


def test_resample_preserves_endpoint_values() -> None:
    df = pd.DataFrame({"t": [0.0, 1.0, 2.0], "altitude": [100.0, 110.0, 130.0]})
    result = resample_to_uniform_time(df, "t", dt=0.5)
    assert math.isclose(result["altitude"].iloc[0], 100.0, rel_tol=1e-9)
    assert math.isclose(result["altitude"].iloc[-1], 130.0, rel_tol=1e-9)


def test_resample_handles_multiple_data_columns() -> None:
    df = pd.DataFrame(
        {"t": [0.0, 1.0, 2.0], "altitude": [100.0, 110.0, 130.0], "mach": [0.5, 0.6, 0.7]}
    )
    result = resample_to_uniform_time(df, "t", dt=1.0)
    assert "altitude" in result.columns
    assert "mach" in result.columns


def test_resample_rejects_missing_time_column() -> None:
    df = pd.DataFrame({"altitude": [100.0, 110.0]})
    with pytest.raises(InvalidFlightDataError):
        resample_to_uniform_time(df, "t", dt=0.5)


def test_resample_rejects_nonpositive_dt() -> None:
    df = pd.DataFrame({"t": [0.0, 1.0], "altitude": [100.0, 110.0]})
    with pytest.raises(InvalidFlightDataError):
        resample_to_uniform_time(df, "t", dt=0)


def test_resample_rejects_non_increasing_time() -> None:
    df = pd.DataFrame({"t": [0.0, 1.0, 0.5], "altitude": [100.0, 110.0, 105.0]})
    with pytest.raises(InvalidFlightDataError):
        resample_to_uniform_time(df, "t", dt=0.5)
