"""GDX Aerospace ecosystem capstone: a small end-to-end mission using many packages.

Run with:
    uv run python examples/11_ecosystem_capstone.py
"""

from __future__ import annotations

import math

from aeromaterials import get_material
from aerostruct import i_beam_properties
from gdxaerospace import list_packages, phase_names
from orbitpy import hohmann_transfer, orbital_period
from sattelemetry import (
    ChannelLimits,
    PacketLayout,
    TelemetryChannel,
    TelemetryDecoder,
    append_crc,
    check_channels,
    pack_primary_header,
)
from stresspy import bending_stress
from uavpy import Multirotor


def ecosystem_overview() -> None:
    """Print a summary of the whole GDX Aerospace ecosystem."""
    print("=== GDX Aerospace ecosystem ===")
    names = phase_names()
    for phase in range(1, 11):
        packages = list_packages(phase=phase)
        print(
            f"Phase {phase:2d} ({names[phase]}): {len(packages)} packages -> "
            f"{', '.join(packages)}"
        )
    print(f"\nTotal packages: {len(list_packages())}")


def small_satellite_mission_demo() -> None:
    """Walk through a tiny cross-package example: structure, orbit, and telemetry."""
    print("\n=== Small satellite mission walk-through ===")

    # Structure: check a simple aluminum bracket under a launch-load bending moment.
    material = get_material("Al7075-T6")
    section = i_beam_properties(
        flange_width=0.02, flange_thickness=0.003, web_height=0.03, web_thickness=0.002
    )
    stress = bending_stress(
        moment=15.0, distance_from_neutral_axis=0.018, moment_of_inertia=section.ixx
    )
    margin = material.yield_strength / stress - 1
    print(f"Bracket bending stress: {stress / 1e6:.1f} MPa (margin of safety: {margin:.1f})")

    # Orbit: a LEO-to-a-slightly-higher-LEO adjustment maneuver.
    leo_radius = 6_778_000.0
    raised_radius = 6_978_000.0
    transfer = hohmann_transfer(leo_radius, raised_radius)
    period = orbital_period(raised_radius)
    print(
        f"Orbit-raise delta-v: {transfer.total_delta_v:.1f} m/s, "
        f"new orbital period: {period / 60:.1f} min"
    )

    # Telemetry: build and decode one housekeeping packet from the "spacecraft."
    layout = PacketLayout(
        name="housekeeping",
        apid=42,
        channels=(
            TelemetryChannel(
                "bus_voltage", 0, "u16", "V", polynomial_coefficients=(0.0, 5.0 / 4095.0)
            ),
        ),
    )
    data = append_crc(bytes([12, 128]))  # raw ADC-like value packed big-endian: 12*256+128=3200
    packet = pack_primary_header(apid=42, data_length=len(data)) + data
    decoded = TelemetryDecoder([layout]).decode(packet)

    limits = {"bus_voltage": ChannelLimits(2.5, 3.0, 4.2, 4.5)}
    statuses = check_channels(decoded.values, limits)
    print(
        f"Decoded bus voltage: {decoded.values['bus_voltage']:.2f} V "
        f"({statuses['bus_voltage'].value})"
    )


def quick_uav_check() -> None:
    """Run a one-line sanity check that the whole install actually works end to end."""
    print("\n=== Quick cross-check ===")
    uav = Multirotor(
        mass=1.2, num_motors=4, rotor_radius=0.09, battery_voltage=14.8, battery_capacity_mah=4000
    )
    print(
        f"Small quad flight time: {uav.flight_time_minutes():.1f} min "
        f"(hover power {uav.hover_power():.1f} W)"
    )
    assert math.isfinite(uav.flight_time_minutes())
    print("All core subsystems installed and importable: OK")


if __name__ == "__main__":
    ecosystem_overview()
    small_satellite_mission_demo()
    quick_uav_check()
