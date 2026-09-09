"""Validate the Aircraft6DOF simulator against physical sanity checks."""

from __future__ import annotations

import math

import pytest
from aircraftsim.aero_model import LinearAeroModel
from aircraftsim.aircraft6dof import Aircraft6DOF
from aircraftsim.exceptions import InvalidAircraftConfigError
from flightdyn.rigid_body import G0


def test_initial_state_matches_constructor_arguments() -> None:
    aircraft = Aircraft6DOF(
        mass=1200.0, inertia=(1500.0, 2000.0, 3000.0), wing_area=16.2,
        initial_altitude=1000.0, initial_airspeed=60.0,
    )
    snap = aircraft.state_snapshot()
    assert math.isclose(snap["altitude"], 1000.0)
    assert math.isclose(snap["airspeed"], 60.0)
    assert math.isclose(snap["roll"], 0.0, abs_tol=1e-9)
    assert math.isclose(snap["pitch"], 0.0, abs_tol=1e-9)
    assert math.isclose(snap["yaw"], 0.0, abs_tol=1e-9)


def test_constructor_rejects_invalid_parameters() -> None:
    with pytest.raises(InvalidAircraftConfigError):
        Aircraft6DOF(mass=0, inertia=(1500.0, 2000.0, 3000.0), wing_area=16.2)
    with pytest.raises(InvalidAircraftConfigError):
        Aircraft6DOF(mass=1200.0, inertia=(1500.0, 0.0, 3000.0), wing_area=16.2)
    with pytest.raises(InvalidAircraftConfigError):
        Aircraft6DOF(mass=1200.0, inertia=(1500.0, 2000.0, 3000.0), wing_area=0)
    with pytest.raises(InvalidAircraftConfigError):
        Aircraft6DOF(mass=1200.0, inertia=(1500.0, 2000.0, 3000.0), wing_area=16.2, max_thrust=0)
    with pytest.raises(InvalidAircraftConfigError):
        Aircraft6DOF(
            mass=1200.0, inertia=(1500.0, 2000.0, 3000.0), wing_area=16.2, initial_altitude=-1.0
        )


def test_step_rejects_nonpositive_dt() -> None:
    aircraft = Aircraft6DOF(mass=1200.0, inertia=(1500.0, 2000.0, 3000.0), wing_area=16.2)
    with pytest.raises(InvalidAircraftConfigError):
        aircraft.step(dt=0)
    with pytest.raises(InvalidAircraftConfigError):
        aircraft.step(dt=-0.01)


def test_free_fall_matches_gravity_when_airspeed_is_zero() -> None:
    """With zero initial airspeed and zero throttle, only gravity acts (no aero force);
    airspeed after a short step should closely match g * dt."""
    aircraft = Aircraft6DOF(
        mass=1000.0, inertia=(1000.0, 1000.0, 1000.0), wing_area=10.0, initial_airspeed=0.0
    )
    state = aircraft.step(dt=0.1, controls={})
    assert math.isclose(state["airspeed"], G0 * 0.1, rel_tol=0.02)


def test_free_fall_loses_altitude() -> None:
    aircraft = Aircraft6DOF(
        mass=1000.0, inertia=(1000.0, 1000.0, 1000.0), wing_area=10.0, initial_airspeed=0.0
    )
    initial_altitude = aircraft.state_snapshot()["altitude"]
    state = aircraft.step(dt=0.1, controls={})
    assert state["altitude"] < initial_altitude


def test_zero_dt_free_body_no_forces_stays_still() -> None:
    """With zero airspeed, zero throttle, at t=0 the derivative test isn't directly
    exposed, but repeated tiny steps should show monotonically increasing fall speed."""
    aircraft = Aircraft6DOF(
        mass=1000.0, inertia=(1000.0, 1000.0, 1000.0), wing_area=10.0, initial_airspeed=0.0
    )
    speeds = []
    for _ in range(5):
        state = aircraft.step(dt=0.05, controls={})
        speeds.append(state["airspeed"])
    assert speeds == sorted(speeds)


def test_symmetric_flight_has_no_lateral_motion() -> None:
    """With zero aileron/rudder and zero initial sideslip, the aircraft should stay
    in the symmetric (roll=0, yaw=0, beta=0) plane -- no lateral-directional coupling."""
    aircraft = Aircraft6DOF(mass=1200.0, inertia=(1500.0, 2000.0, 3000.0), wing_area=16.2)
    for _ in range(200):
        state = aircraft.step(dt=0.01, controls={"throttle": 0.6})
    assert math.isclose(state["roll"], 0.0, abs_tol=1e-9)
    assert math.isclose(state["yaw"], 0.0, abs_tol=1e-9)
    assert math.isclose(state["beta"], 0.0, abs_tol=1e-9)
    assert math.isclose(state["east"], 0.0, abs_tol=1e-6)


def test_positive_throttle_increases_airspeed_over_time() -> None:
    aircraft = Aircraft6DOF(mass=1200.0, inertia=(1500.0, 2000.0, 3000.0), wing_area=16.2)
    initial_speed = aircraft.state_snapshot()["airspeed"]
    for _ in range(300):
        state = aircraft.step(dt=0.01, controls={"throttle": 0.9})
    assert state["airspeed"] > initial_speed


def test_positive_aileron_induces_roll_rate() -> None:
    """A positive aileron deflection should produce a nonzero roll rate (rolling moment)."""
    aircraft = Aircraft6DOF(mass=1200.0, inertia=(1500.0, 2000.0, 3000.0), wing_area=16.2)
    state = aircraft.step(dt=0.01, controls={"aileron": 0.1, "throttle": 0.6})
    assert state["p"] != 0.0


def test_positive_rudder_induces_yaw_rate() -> None:
    aircraft = Aircraft6DOF(mass=1200.0, inertia=(1500.0, 2000.0, 3000.0), wing_area=16.2)
    state = aircraft.step(dt=0.01, controls={"rudder": 0.1, "throttle": 0.6})
    assert state["r"] != 0.0


def test_quaternion_stays_normalized_over_many_steps() -> None:
    """Renormalization each step should keep the internal quaternion at unit norm."""
    import numpy as np

    aircraft = Aircraft6DOF(mass=1200.0, inertia=(1500.0, 2000.0, 3000.0), wing_area=16.2)
    for _ in range(1000):
        aircraft.step(dt=0.01, controls={"elevator": 0.02, "aileron": 0.01, "throttle": 0.7})
    quat = aircraft._state[6:10]
    assert math.isclose(float(np.linalg.norm(quat)), 1.0, abs_tol=1e-9)


def test_custom_aero_model_is_used() -> None:
    """A custom LinearAeroModel with zero lift/drag should behave differently from default."""
    zero_lift_model = LinearAeroModel(cl0=0.0, cl_alpha=0.0, cd0=0.0, induced_drag_factor=0.0)
    aircraft = Aircraft6DOF(
        mass=1200.0, inertia=(1500.0, 2000.0, 3000.0), wing_area=16.2, aero=zero_lift_model
    )
    # With no lift and no drag, and thrust along +X, the aircraft should simply
    # accelerate forward and begin to droop under gravity (no lift to hold it up).
    initial_alt = aircraft.state_snapshot()["altitude"]
    for _ in range(200):
        state = aircraft.step(dt=0.01, controls={"throttle": 0.6})
    assert state["altitude"] < initial_alt
