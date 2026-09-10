"""Satellite telemetry demo: build, decode, limit-check, and archive packets.

Run with:
    uv run python examples/07_satellite_telemetry.py
"""

from __future__ import annotations

import random
import struct

from sattelemetry import (
    ChannelLimits,
    PacketLayout,
    TelemetryArchive,
    TelemetryChannel,
    TelemetryDecoder,
    append_crc,
    check_channels,
    pack_primary_header,
)


def build_housekeeping_packet(battery_raw: int, temp_raw: int) -> bytes:
    """Build a raw housekeeping packet, matching the layout defined below."""
    data_field = struct.pack(">Hh", battery_raw, temp_raw)
    data_with_crc = append_crc(data_field)
    header = pack_primary_header(apid=100, data_length=len(data_with_crc))
    return header + data_with_crc


def main() -> None:
    """Run the telemetry pass simulation and print flagged anomalies."""
    layout = PacketLayout(
        name="housekeeping",
        apid=100,
        channels=(
            TelemetryChannel(
                "battery_voltage",
                byte_offset=0,
                raw_type="u16",
                units="V",
                polynomial_coefficients=(0.0, 5.0 / 4095.0),
            ),
            TelemetryChannel(
                "temperature",
                byte_offset=2,
                raw_type="i16",
                units="degC",
                polynomial_coefficients=(0.0, 0.01),
            ),
        ),
    )
    limits = {
        "battery_voltage": ChannelLimits(
            red_low=2.5, yellow_low=3.0, yellow_high=4.2, red_high=4.5
        ),
        "temperature": ChannelLimits(
            red_low=-20.0, yellow_low=-10.0, yellow_high=40.0, red_high=50.0
        ),
    }

    decoder = TelemetryDecoder([layout])
    archive = TelemetryArchive()

    print("=== Simulating a telemetry pass ===")
    random.seed(42)
    for t in range(20):
        # Simulate a slowly discharging battery with noise, and one clear anomaly.
        battery_raw = int(3200 - t * 15 + random.uniform(-10, 10))
        temp_raw = int(1500 + random.uniform(-50, 50))
        if t == 15:
            battery_raw = 1800  # simulated undervoltage anomaly

        packet = build_housekeeping_packet(battery_raw, temp_raw)
        decoded = decoder.decode(packet)
        archive.add(timestamp=float(t), values=decoded.values)

        statuses = check_channels(decoded.values, limits)
        flags = ", ".join(
            f"{name}={status.value}"
            for name, status in statuses.items()
            if status.value != "nominal"
        )
        if flags:
            print(f"t={t:2d}s: battery={decoded.values['battery_voltage']:.2f} V  [{flags}]")

    print(f"\nArchived {len(archive)} records across channels: {sorted(archive.channels())}")

    print("\n=== Statistical outlier check ===")
    outliers = archive.detect_outliers("battery_voltage", z_threshold=2.5)
    for record in outliers:
        print(f"Outlier at t={record.timestamp:.0f}s: battery_voltage={record.value:.2f} V")


if __name__ == "__main__":
    main()
