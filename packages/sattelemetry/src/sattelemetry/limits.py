"""Red/yellow limit checking, the standard telemetry anomaly-detection method.

Reference
---------
- This "red/yellow limits" scheme (a value inside its expected band is
  nominal; outside a yellow band is a caution; outside a red band is an
  alarm) is the standard first-line anomaly detection method used across
  spacecraft operations centers and ground-system software.

Assumptions
-----------
- Static limits only (fixed bounds), not the more elaborate
  "expected state" or "delta" checking (where limits depend on
  spacecraft mode or rate of change) that operational systems often add
  on top of static limits.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from sattelemetry.exceptions import InvalidPacketError


class LimitStatus(Enum):
    """The status of a telemetry value against its configured limits."""

    NOMINAL = "nominal"
    YELLOW_LOW = "yellow_low"
    YELLOW_HIGH = "yellow_high"
    RED_LOW = "red_low"
    RED_HIGH = "red_high"


@dataclass(frozen=True)
class ChannelLimits:
    """Red/yellow limits for one telemetry channel.

    Parameters
    ----------
    red_low, yellow_low:
        Lower alarm and caution thresholds. ``red_low <= yellow_low``.
    yellow_high, red_high:
        Upper caution and alarm thresholds. ``yellow_high <= red_high``.

    """

    red_low: float
    yellow_low: float
    yellow_high: float
    red_high: float

    def __post_init__(self) -> None:
        if not (self.red_low <= self.yellow_low <= self.yellow_high <= self.red_high):
            raise InvalidPacketError(
                "limits must satisfy red_low <= yellow_low <= yellow_high <= red_high, "
                f"got ({self.red_low}, {self.yellow_low}, {self.yellow_high}, {self.red_high})"
            )

    def check(self, value: float) -> LimitStatus:
        """Classify ``value`` against these limits.

        Parameters
        ----------
        value:
            The telemetry value to check.

        Returns
        -------
        LimitStatus

        Example
        -------
        >>> limits = ChannelLimits(red_low=2.5, yellow_low=3.0, yellow_high=4.2, red_high=4.5)
        >>> limits.check(3.5)
        <LimitStatus.NOMINAL: 'nominal'>
        >>> limits.check(2.8)
        <LimitStatus.YELLOW_LOW: 'yellow_low'>
        >>> limits.check(2.0)
        <LimitStatus.RED_LOW: 'red_low'>

        """
        if value < self.red_low:
            return LimitStatus.RED_LOW
        if value < self.yellow_low:
            return LimitStatus.YELLOW_LOW
        if value > self.red_high:
            return LimitStatus.RED_HIGH
        if value > self.yellow_high:
            return LimitStatus.YELLOW_HIGH
        return LimitStatus.NOMINAL


def check_channels(
    values: dict[str, float], limits: dict[str, ChannelLimits]
) -> dict[str, LimitStatus]:
    """Check multiple named channel values against their configured limits.

    Channels in ``values`` with no entry in ``limits`` are skipped (not
    an error) -- not every telemetry point needs limits defined.

    Parameters
    ----------
    values:
        Channel name -> value, e.g. from
        :attr:`sattelemetry.decoder.DecodedPacket.values`.
    limits:
        Channel name -> :class:`ChannelLimits`, for the channels that
        have limits defined.

    Returns
    -------
    dict[str, LimitStatus]
        Status for each channel that had limits defined.

    Example
    -------
    >>> limits = {"battery_voltage": ChannelLimits(2.5, 3.0, 4.2, 4.5)}
    >>> check_channels({"battery_voltage": 2.0, "temperature": 20.0}, limits)
    {'battery_voltage': <LimitStatus.RED_LOW: 'red_low'>}

    """
    return {name: limits[name].check(value) for name, value in values.items() if name in limits}
