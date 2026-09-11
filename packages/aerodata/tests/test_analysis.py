"""Validate descriptive statistics and z-score outlier detection."""

from __future__ import annotations

import math

import pandas as pd
import pytest
from aerodata.analysis import descriptive_stats, detect_outliers_zscore
from aerodata.exceptions import InvalidFlightDataError


def test_descriptive_stats_matches_pandas_directly() -> None:
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    stats = descriptive_stats(s)
    assert math.isclose(stats.mean, s.mean(), rel_tol=1e-9)
    assert math.isclose(stats.std, s.std(), rel_tol=1e-9)
    assert math.isclose(stats.minimum, s.min(), rel_tol=1e-9)
    assert math.isclose(stats.maximum, s.max(), rel_tol=1e-9)
    assert math.isclose(stats.median, s.median(), rel_tol=1e-9)


def test_descriptive_stats_ignores_nan_values() -> None:
    s = pd.Series([1.0, 2.0, float("nan"), 3.0])
    stats = descriptive_stats(s)
    assert math.isclose(stats.mean, 2.0, rel_tol=1e-9)


def test_descriptive_stats_rejects_all_nan_series() -> None:
    s = pd.Series([float("nan"), float("nan")])
    with pytest.raises(InvalidFlightDataError):
        descriptive_stats(s)


def test_detect_outliers_zscore_flags_clear_outlier() -> None:
    s = pd.Series([10.0, 10.1, 9.9, 10.0, 9.8, 10.2, 9.9, 10.1, 9.8, 10.0, 50.0])
    mask = detect_outliers_zscore(s)
    assert mask.iloc[-1]
    assert not mask.iloc[:-1].any()


def test_detect_outliers_zscore_no_outliers_in_uniform_data() -> None:
    s = pd.Series([10.0, 10.1, 9.9, 10.0, 9.8, 10.2])
    mask = detect_outliers_zscore(s)
    assert not mask.any()


def test_detect_outliers_zscore_empty_mask_for_constant_series() -> None:
    """Zero variance means nothing can be a statistical outlier."""
    s = pd.Series([5.0, 5.0, 5.0, 5.0])
    mask = detect_outliers_zscore(s)
    assert not mask.any()


def test_detect_outliers_zscore_empty_mask_for_short_series() -> None:
    s = pd.Series([5.0])
    mask = detect_outliers_zscore(s)
    assert not mask.any()


def test_detect_outliers_zscore_respects_custom_threshold() -> None:
    s = pd.Series([10.0, 10.1, 9.9, 10.0, 12.0])
    strict = detect_outliers_zscore(s, threshold=1.0)
    lenient = detect_outliers_zscore(s, threshold=5.0)
    assert strict.sum() >= lenient.sum()


def test_detect_outliers_zscore_rejects_nonpositive_threshold() -> None:
    s = pd.Series([1.0, 2.0, 3.0])
    with pytest.raises(InvalidFlightDataError):
        detect_outliers_zscore(s, threshold=0)
    with pytest.raises(InvalidFlightDataError):
        detect_outliers_zscore(s, threshold=-1.0)


def test_detect_outliers_zscore_mask_same_index_as_input() -> None:
    s = pd.Series([1.0, 2.0, 3.0], index=[10, 20, 30])
    mask = detect_outliers_zscore(s)
    assert list(mask.index) == [10, 20, 30]
