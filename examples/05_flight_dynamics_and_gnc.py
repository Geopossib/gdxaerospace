"""Aircraft simulation, autopilot, guidance, navigation, and estimation demo.

Flies a modest closed-loop altitude-hold climb, demonstrates heading-hold
in isolation, then runs standalone guidance/navigation/estimation demos.

Run with:
    uv run python examples/05_flight_dynamics_and_gnc.py
"""

from __future__ import annotations

import math

import numpy as np
from guidancepy.proportional_navigation import closing_velocity, line_of_sight_rate

from aircraftsim import Aircraft6DOF
from autopilotpy import AltitudeHoldAutopilot, HeadingHoldAutopilot
from guidancepy import proportional_navigation_command
from kalmanflight import KalmanFilter
from navigationpy import great_circle_distance, initial_bearing


def autopilot_flight_demo() -> None:
    """Fly a modest climb using altitude-hold in closed loop with the aircraft.

    Note: only altitude-hold is flown in closed loop here. Heading-hold is
    demonstrated separately, in isolation, below -- this simplified linear
    aero model's lateral-directional dynamics (see
    ``aircraftsim.aero_model``'s documented small-sideslip assumption) are
    not damped enough for a well-behaved closed-loop turn without more
    careful tuning than a demo script should paper over; that is a real
    control-engineering exercise, not something to fake here.
    """
    aircraft = Aircraft6DOF(mass=1200.0, inertia=(1500.0, 2000.0, 3000.0), wing_area=16.2)
    altitude_ap = AltitudeHoldAutopilot()

    target_altitude = 1050.0
    dt = 0.05

    print("=== Autopilot flight demo: altitude hold (closed loop) ===")
    for step in range(400):
        snap = aircraft.state_snapshot()
        elevator = altitude_ap.command(snap["altitude"], target_altitude, dt)
        snap = aircraft.step(dt=dt, controls={"elevator": elevator, "throttle": 0.7})
        if step % 100 == 0:
            print(
                f"t={step * dt:5.1f}s  alt={snap['altitude']:7.1f} m  "
                f"pitch={math.degrees(snap['pitch']):6.1f} deg  "
                f"airspeed={snap['airspeed']:5.1f} m/s"
            )
    print(f"Final: alt={snap['altitude']:.1f} m (target {target_altitude})")

    print("\n=== Heading-hold PID: isolated demo (not closed-loop with the aircraft) ===")
    heading_ap = HeadingHoldAutopilot()
    for current_deg, target_deg in [(0, 15), (350, 10), (90, 85)]:
        aileron = heading_ap.command(
            math.radians(current_deg), math.radians(target_deg), dt=0.05
        )
        print(
            f"current={current_deg:>4} deg, target={target_deg:>4} deg -> "
            f"aileron={aileron:+.4f} rad"
        )


def guidance_navigation_estimation_demo() -> None:
    """Compute a great-circle route, a PN intercept command, and fuse noisy tracking data."""
    print("\n=== Navigation: great-circle route ===")
    jfk = (math.radians(40.6413), math.radians(-73.7781))
    lhr = (math.radians(51.4700), math.radians(-0.4543))
    distance_km = great_circle_distance(*jfk, *lhr) / 1000
    bearing_deg = math.degrees(initial_bearing(*jfk, *lhr))
    print(f"JFK -> LHR: {distance_km:.0f} km, initial bearing {bearing_deg:.1f} deg true")

    print("\n=== Guidance: proportional navigation ===")
    relative_position = np.array([2000.0, 500.0])
    relative_velocity = np.array([-250.0, 30.0])
    vc = closing_velocity(relative_position, relative_velocity)
    los_rate = line_of_sight_rate(relative_position, relative_velocity)
    a_cmd = proportional_navigation_command(vc, los_rate, navigation_constant=4.0)
    print(f"Closing velocity: {vc:.1f} m/s, LOS rate: {math.degrees(los_rate):.3f} deg/s")
    print(f"PN lateral acceleration command: {a_cmd:.2f} m/s^2")

    print("\n=== Estimation: constant-velocity Kalman tracker ===")
    dt = 1.0
    f = np.array([[1.0, dt], [0.0, 1.0]])
    h = np.array([[1.0, 0.0]])
    q = np.array([[0.01, 0.0], [0.0, 0.01]])
    r = np.array([[4.0]])
    kf = KalmanFilter(x0=np.array([0.0, 0.0]), p0=np.eye(2) * 100.0, f=f, h=h, q=q, r=r)

    true_position, true_velocity = 0.0, 15.0
    rng = np.random.default_rng(7)
    for _ in range(30):
        true_position += true_velocity * dt
        measurement = true_position + rng.normal(0, 2.0)
        kf.predict()
        kf.update(np.array([measurement]))
    print(
        f"Estimated position/velocity: {kf.x[0]:.1f} m, {kf.x[1]:.2f} m/s "
        f"(true: {true_position:.1f} m, {true_velocity:.1f} m/s)"
    )


if __name__ == "__main__":
    autopilot_flight_demo()
    guidance_navigation_estimation_demo()
