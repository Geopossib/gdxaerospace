"""Validate red/yellow limit checking."""

from __future__ import annotations

import pytest
from sattelemetry.exceptions import InvalidPacketError
from sattelemetry.limits import ChannelLimits, LimitStatus, check_channels


@pytest.fixture
def limits() -> ChannelLimits:
    return ChannelLimits(red_low=2.5, yellow_low=3.0, yellow_high=4.2, red_high=4.5)


def test_nominal_value(limits: ChannelLimits) -> None:
    assert limits.check(3.5) == LimitStatus.NOMINAL


def test_boundary_values_are_nominal(limits: ChannelLimits) -> None:
    """Exactly at yellow_low/yellow_high should be nominal (yellow requires strictly beyond)."""
    assert limits.check(3.0) == LimitStatus.NOMINAL
    assert limits.check(4.2) == LimitStatus.NOMINAL


def test_yellow_low(limits: ChannelLimits) -> None:
    assert limits.check(2.8) == LimitStatus.YELLOW_LOW


def test_yellow_high(limits: ChannelLimits) -> None:
    assert limits.check(4.3) == LimitStatus.YELLOW_HIGH


def test_red_low(limits: ChannelLimits) -> None:
    assert limits.check(2.0) == LimitStatus.RED_LOW


def test_red_high(limits: ChannelLimits) -> None:
    assert limits.check(5.0) == LimitStatus.RED_HIGH


def test_red_low_boundary(limits: ChannelLimits) -> None:
    """Exactly at red_low is not < red_low, so it's yellow; strictly below is red."""
    assert limits.check(2.5) == LimitStatus.YELLOW_LOW
    assert limits.check(2.49) == LimitStatus.RED_LOW


def test_channel_limits_rejects_invalid_ordering() -> None:
    with pytest.raises(InvalidPacketError):
        ChannelLimits(red_low=3.0, yellow_low=2.5, yellow_high=4.2, red_high=4.5)
    with pytest.raises(InvalidPacketError):
        ChannelLimits(red_low=2.5, yellow_low=3.0, yellow_high=4.5, red_high=4.2)


def test_check_channels_skips_channels_without_limits(limits: ChannelLimits) -> None:
    result = check_channels(
        {"battery_voltage": 2.0, "temperature": 20.0}, {"battery_voltage": limits}
    )
    assert result == {"battery_voltage": LimitStatus.RED_LOW}
    assert "temperature" not in result


def test_check_channels_empty_limits_returns_empty() -> None:
    result = check_channels({"battery_voltage": 2.0}, {})
    assert result == {}
