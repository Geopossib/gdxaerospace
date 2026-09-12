"""Validate vertical rocket trajectory simulation."""

from __future__ import annotations

import bisect
import math

import pytest
from rockettraj.exceptions import InvalidTrajectoryInputError
from rockettraj.trajectory import G0, RocketConfig, simulate_trajectory


def _make_config(**overrides: float) -> RocketConfig:
    defaults = {
        "dry_mass": 5.0,
        "propellant_mass": 2.0,
        "burn_time": 3.0,
        "thrust": 200.0,
        "drag_coefficient": 0.5,
        "reference_area": 0.01,
    }
    defaults.update(overrides)
    return RocketConfig(**defaults)


def test_mass_at_start_equals_wet_mass() -> None:
    config = _make_config()
    assert math.isclose(config.mass_at(0.0), 7.0, rel_tol=1e-9)


def test_mass_at_burnout_equals_dry_mass() -> None:
    config = _make_config()
    assert math.isclose(config.mass_at(config.burn_time), config.dry_mass, rel_tol=1e-9)
    assert math.isclose(config.mass_at(config.burn_time + 10.0), config.dry_mass, rel_tol=1e-9)


def test_mass_depletes_linearly_during_burn() -> None:
    config = _make_config()
    mid_burn_mass = config.mass_at(1.5)
    expected = config.dry_mass + config.propellant_mass / 2
    assert math.isclose(mid_burn_mass, expected, rel_tol=1e-9)


def test_thrust_at_zero_after_burnout() -> None:
    config = _make_config()
    assert config.thrust_at(config.burn_time) == 0.0
    assert config.thrust_at(config.burn_time + 1.0) == 0.0
    assert config.thrust_at(0.0) == config.thrust


def test_rocket_config_rejects_nonpositive_inputs() -> None:
    with pytest.raises(InvalidTrajectoryInputError):
        _make_config(dry_mass=0)
    with pytest.raises(InvalidTrajectoryInputError):
        _make_config(propellant_mass=-1.0)
    with pytest.raises(InvalidTrajectoryInputError):
        _make_config(burn_time=0)
    with pytest.raises(InvalidTrajectoryInputError):
        _make_config(thrust=0)
    with pytest.raises(InvalidTrajectoryInputError):
        _make_config(drag_coefficient=0)
    with pytest.raises(InvalidTrajectoryInputError):
        _make_config(reference_area=0)


def test_simulate_trajectory_reaches_positive_apogee() -> None:
    config = _make_config()
    result = simulate_trajectory(config)
    assert result.apogee_altitude > 0


def test_simulate_trajectory_starts_at_ground() -> None:
    config = _make_config()
    result = simulate_trajectory(config)
    assert result.altitudes[0] == 0.0
    assert result.velocities[0] == 0.0


def test_simulate_trajectory_ends_near_ground() -> None:
    """The simulation should terminate close to ground impact (altitude near zero)."""
    config = _make_config()
    result = simulate_trajectory(config)
    assert abs(result.altitudes[-1]) < 50.0  # within one time-step's worth of altitude change


def test_simulate_trajectory_apogee_occurs_after_burnout() -> None:
    config = _make_config()
    result = simulate_trajectory(config)
    assert result.apogee_time > config.burn_time


def test_simulate_trajectory_mass_decreases_only_during_burn() -> None:
    config = _make_config()
    result = simulate_trajectory(config)
    burnout_index = bisect.bisect_left(result.times, config.burn_time)
    # Mass should be strictly decreasing before burnout...
    assert result.masses[0] > result.masses[burnout_index]
    # ...and settle at (very close to) dry mass after -- fixed-step RK4 has a small,
    # expected mass-conservation error right at the burn_time discontinuity (see the
    # module docstring), so this uses a loose tolerance rather than exact equality.
    assert math.isclose(result.masses[-1], config.dry_mass, rel_tol=1e-2)


def test_simulate_trajectory_matches_closed_form_with_negligible_drag() -> None:
    """With negligible drag, post-burnout coast should match simple kinematics:
    apogee = burnout_altitude + v_burnout^2 / (2*g0)."""
    config = _make_config(drag_coefficient=1e-9, reference_area=1e-9)
    result = simulate_trajectory(config)
    burnout_index = bisect.bisect_left(result.times, config.burn_time)
    v_burnout = result.velocities[burnout_index]
    alt_burnout = result.altitudes[burnout_index]
    predicted_apogee = alt_burnout + v_burnout**2 / (2 * G0)
    assert math.isclose(predicted_apogee, result.apogee_altitude, rel_tol=1e-4)


def test_simulate_trajectory_more_drag_reduces_apogee() -> None:
    low_drag = simulate_trajectory(_make_config(drag_coefficient=0.1))
    high_drag = simulate_trajectory(_make_config(drag_coefficient=1.0))
    assert high_drag.apogee_altitude < low_drag.apogee_altitude


def test_simulate_trajectory_more_thrust_increases_apogee() -> None:
    low_thrust = simulate_trajectory(_make_config(thrust=150.0))
    high_thrust = simulate_trajectory(_make_config(thrust=300.0))
    assert high_thrust.apogee_altitude > low_thrust.apogee_altitude


def test_simulate_trajectory_rejects_nonpositive_dt() -> None:
    config = _make_config()
    with pytest.raises(InvalidTrajectoryInputError):
        simulate_trajectory(config, dt=0)


def test_simulate_trajectory_rejects_nonpositive_max_time() -> None:
    config = _make_config()
    with pytest.raises(InvalidTrajectoryInputError):
        simulate_trajectory(config, max_time=0)
