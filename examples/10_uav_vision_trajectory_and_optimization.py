"""UAV sizing, edge detection, rocket trajectory, and design optimization demo.

Run with:
    uv run python examples/10_uav_vision_trajectory_and_optimization.py
"""

from __future__ import annotations

import numpy as np

from aeroopt import optimize_aspect_ratio
from aerovision import detect_linear_features, gradient_magnitude
from rockettraj import RocketConfig, simulate_trajectory
from uavpy import Multirotor, stall_speed, wing_loading


def uav_sizing_demo() -> None:
    """Size a small quadcopter and a small fixed-wing UAV."""
    print("=== UAV sizing ===")
    quad = Multirotor(
        mass=2.5,
        num_motors=4,
        rotor_radius=0.127,
        battery_voltage=22.2,
        battery_capacity_mah=5000,
    )
    print(f"Quadcopter hover power: {quad.hover_power():.1f} W")
    print(f"Quadcopter estimated flight time: {quad.flight_time_minutes():.1f} min")

    weight = 9.81 * 10.0  # 10 kg fixed-wing UAV
    wing_area = 0.6
    print(f"\nFixed-wing wing loading: {wing_loading(weight, wing_area):.1f} Pa")
    print(
        "Fixed-wing stall speed: "
        f"{stall_speed(weight, wing_area, max_lift_coefficient=1.3):.1f} m/s"
    )


def vision_demo() -> None:
    """Highlight a synthetic crack-like linear feature in a noisy image."""
    print("\n=== Classical edge/crack detection ===")
    rng = np.random.default_rng(3)
    image = rng.normal(0.5, 0.02, size=(20, 20))
    image[10, 5:15] = 0.9  # a synthetic horizontal "crack"

    mag = gradient_magnitude(image)
    mask = detect_linear_features(image, threshold=0.3)
    print(f"Max gradient magnitude: {mag.max():.2f}")
    print(f"Flagged pixels: {mask.sum()} out of {mask.size}")


def rocket_trajectory_demo() -> None:
    """Simulate a small sounding rocket's flight to apogee."""
    print("\n=== Rocket trajectory ===")
    config = RocketConfig(
        dry_mass=5.0,
        propellant_mass=2.0,
        burn_time=3.0,
        thrust=200.0,
        drag_coefficient=0.5,
        reference_area=0.01,
    )
    result = simulate_trajectory(config)
    print(f"Apogee altitude: {result.apogee_altitude:.1f} m at t={result.apogee_time:.1f} s")
    print(f"Total flight time: {result.times[-1]:.1f} s")


def optimization_demo() -> None:
    """Find the drag-minimizing wing aspect ratio for a simplified design tradeoff."""
    print("\n=== Design optimization ===")
    result = optimize_aspect_ratio(lift_coefficient=0.5, parasitic_drag_coefficient=0.02)
    print(f"Optimal aspect ratio: {result.x:.2f}")
    print(f"Minimum total drag coefficient: {result.fun:.4f}")


if __name__ == "__main__":
    uav_sizing_demo()
    vision_demo()
    rocket_trajectory_demo()
    optimization_demo()
