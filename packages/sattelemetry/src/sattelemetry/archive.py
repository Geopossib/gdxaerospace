"""A simple, queryable in-memory telemetry archive with basic statistical anomaly detection.

Reference
---------
- Storing decoded telemetry as a time-ordered series per channel, then
  screening for statistical outliers, is standard practice for
  post-pass telemetry review (distinct from real-time red/yellow limit
  checking in :mod:`sattelemetry.limits`, which flags values as they
  arrive against fixed, pre-defined bounds).

Assumptions
-----------
- In-memory only: this is meant for a single ground-pass or analysis
  session, not a persistent telemetry database. For long-term storage,
  export :meth:`TelemetryArchive.series` to your own database/file
  format.
- The z-score outlier detector assumes an approximately Gaussian
  distribution for the channel; it is a simple, general-purpose first
  screen, not a substitute for a channel-specific anomaly model. A
  single extreme outlier in a short series can inflate the standard
  deviation enough to mask itself (a well-known z-score limitation) --
  this detector is most reliable with a reasonably long, mostly-nominal
  series behind each check.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass

from sattelemetry.exceptions import InvalidPacketError


@dataclass(frozen=True)
class TelemetryRecord:
    """One timestamped telemetry sample."""

    timestamp: float
    """Seconds since an arbitrary reference epoch (caller-defined)."""
    channel: str
    value: float


class TelemetryArchive:
    """An in-memory, time-ordered archive of decoded telemetry, queryable by channel."""

    def __init__(self) -> None:
        self._records: list[TelemetryRecord] = []

    def add(self, timestamp: float, values: dict[str, float]) -> None:
        """Add one packet's worth of calibrated channel values at a given timestamp.

        Parameters
        ----------
        timestamp:
            Seconds since an arbitrary reference epoch.
        values:
            Channel name -> value, e.g. from
            :attr:`sattelemetry.decoder.DecodedPacket.values`.

        """
        for channel, value in values.items():
            self._records.append(TelemetryRecord(timestamp, channel, value))

    def series(self, channel: str) -> list[TelemetryRecord]:
        """Return all records for one channel, in the order they were added.

        Parameters
        ----------
        channel:
            Channel name.

        Returns
        -------
        list[TelemetryRecord]

        Example
        -------
        >>> archive = TelemetryArchive()
        >>> archive.add(0.0, {"battery_voltage": 3.9})
        >>> archive.add(1.0, {"battery_voltage": 3.8})
        >>> [r.value for r in archive.series("battery_voltage")]
        [3.9, 3.8]

        """
        return [r for r in self._records if r.channel == channel]

    def channels(self) -> set[str]:
        """Return the set of channel names present in the archive."""
        return {r.channel for r in self._records}

    def __len__(self) -> int:
        return len(self._records)

    def detect_outliers(
        self, channel: str, *, z_threshold: float = 3.0
    ) -> list[TelemetryRecord]:
        """Flag statistically outlying records for one channel.

        A record is flagged when its value is more than ``z_threshold``
        standard deviations from the channel's mean -- a simple
        first-pass statistical anomaly screen.

        Parameters
        ----------
        channel:
            Channel name.
        z_threshold:
            Number of standard deviations from the mean to flag, > 0.
            Defaults to 3.0 (a common conventional threshold, ~0.3%
            false-positive rate under a Gaussian assumption).

        Returns
        -------
        list[TelemetryRecord]
            The flagged records, in their original order. Returns an
            empty list if the channel has fewer than 2 records (not
            enough data to compute a meaningful standard deviation) or
            zero variance (all values identical -- nothing is an outlier).

        Example
        -------
        >>> archive = TelemetryArchive()
        >>> readings = [3.9, 3.91, 3.89, 3.90, 3.92, 3.88, 3.91, 3.89, 3.90, 3.92, 1.0]
        >>> for v in readings:  # last value is a clear outlier
        ...     archive.add(0.0, {"battery_voltage": v})
        >>> outliers = archive.detect_outliers("battery_voltage")
        >>> [r.value for r in outliers]
        [1.0]

        """
        if z_threshold <= 0:
            raise InvalidPacketError(f"z_threshold must be positive, got {z_threshold!r}")
        records = self.series(channel)
        if len(records) < 2:
            return []
        values = [r.value for r in records]
        mean = statistics.fmean(values)
        stdev = statistics.pstdev(values, mu=mean)
        if stdev == 0:
            return []
        return [r for r in records if abs(r.value - mean) / stdev > z_threshold]
