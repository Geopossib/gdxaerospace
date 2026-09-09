"""Validate the PID controller (with anti-windup) and hold-mode autopilots."""

from __future__ import annotations

import math

import pytest
from autopilotpy.exceptions import InvalidControllerConfigError
from autopilotpy.hold_modes import AltitudeHoldAutopilot, HeadingHoldAutopilot, heading_error
from autopilotpy.pid import PIDController


def test_p_only_controller_matches_proportional_formula() -> None:
    pid = PIDController(kp=2.0, ki=0.0, kd=0.0)
    assert pid.update(error=3.0, dt=0.1) == 6.0


def test_i_only_controller_accumulates_over_steps() -> None:
    pid = PIDController(kp=0.0, ki=1.0, kd=0.0)
    out1 = pid.update(error=2.0, dt=0.1)  # integral = 0.2
    out2 = pid.update(error=2.0, dt=0.1)  # integral = 0.4
    assert math.isclose(out1, 0.2, rel_tol=1e-9)
    assert math.isclose(out2, 0.4, rel_tol=1e-9)


def test_d_only_controller_matches_derivative_formula() -> None:
    pid = PIDController(kp=0.0, ki=0.0, kd=1.0)
    pid.update(error=1.0, dt=0.1)
    out2 = pid.update(error=3.0, dt=0.1)  # derivative = (3-1)/0.1 = 20
    assert math.isclose(out2, 20.0, rel_tol=1e-9)


def test_d_term_zero_on_first_call() -> None:
    """With no previous error, the derivative term is defined as zero, not undefined."""
    pid = PIDController(kp=0.0, ki=0.0, kd=1.0)
    assert pid.update(error=5.0, dt=0.1) == 0.0


def test_pid_rejects_nonpositive_dt() -> None:
    pid = PIDController(kp=1.0, ki=0.0, kd=0.0)
    with pytest.raises(InvalidControllerConfigError):
        pid.update(error=1.0, dt=0)


def test_pid_rejects_invalid_output_limits() -> None:
    with pytest.raises(InvalidControllerConfigError):
        PIDController(1.0, 0.0, 0.0, output_limits=(1.0, 1.0))
    with pytest.raises(InvalidControllerConfigError):
        PIDController(1.0, 0.0, 0.0, output_limits=(2.0, 1.0))


def test_output_clamped_to_limits() -> None:
    pid = PIDController(kp=10.0, ki=0.0, kd=0.0, output_limits=(-1.0, 1.0))
    assert pid.update(error=5.0, dt=0.1) == 1.0
    assert pid.update(error=-5.0, dt=0.1) == -1.0


def test_anti_windup_freezes_integral_when_saturating() -> None:
    """With a large constant error that saturates the output, the integral must not
    keep growing unboundedly -- it should freeze once saturated."""
    pid = PIDController(kp=0.0, ki=1.0, kd=0.0, output_limits=(-1.0, 1.0))
    for _ in range(100):
        pid.update(error=5.0, dt=0.1)
    frozen_integral = pid._integral
    for _ in range(100):
        pid.update(error=5.0, dt=0.1)
    assert math.isclose(pid._integral, frozen_integral, rel_tol=1e-9)


def test_anti_windup_allows_recovery_after_error_reverses() -> None:
    """After the error reverses sign, the (frozen) integral should immediately start
    shrinking again rather than staying stuck (this is what prevents overshoot)."""
    pid = PIDController(kp=0.0, ki=1.0, kd=0.0, output_limits=(-1.0, 1.0))
    for _ in range(50):
        pid.update(error=5.0, dt=0.1)
    saturated_integral = pid._integral
    pid.update(error=-5.0, dt=0.1)
    assert pid._integral < saturated_integral


def test_reset_clears_integral_and_derivative_history() -> None:
    pid = PIDController(kp=0.0, ki=1.0, kd=1.0)
    pid.update(error=5.0, dt=0.1)
    pid.reset()
    # After reset, derivative term should again be zero on the first call (no history).
    out = pid.update(error=5.0, dt=0.1)
    assert math.isclose(out, 0.5, rel_tol=1e-9)  # only the (now-fresh) integral term


def test_heading_error_wraps_across_boundary() -> None:
    err = heading_error(math.radians(350), math.radians(10))
    assert math.isclose(math.degrees(err), 20.0, abs_tol=1e-9)


def test_heading_error_no_wrap_needed() -> None:
    err = heading_error(math.radians(10), math.radians(30))
    assert math.isclose(math.degrees(err), 20.0, abs_tol=1e-9)


def test_heading_error_negative_direction() -> None:
    err = heading_error(math.radians(30), math.radians(10))
    assert math.isclose(math.degrees(err), -20.0, abs_tol=1e-9)


def test_heading_error_at_180_degrees() -> None:
    err = heading_error(0.0, math.pi)
    assert math.isclose(abs(err), math.pi, abs_tol=1e-9)


def test_altitude_hold_commands_nose_up_when_below_target() -> None:
    """Climbing requires negative elevator (Cm_elevator < 0: positive elevator = nose down)."""
    ap = AltitudeHoldAutopilot()
    command = ap.command(current_altitude=900.0, target_altitude=1000.0, dt=0.1)
    assert command < 0


def test_altitude_hold_commands_nose_down_when_above_target() -> None:
    ap = AltitudeHoldAutopilot()
    command = ap.command(current_altitude=1100.0, target_altitude=1000.0, dt=0.1)
    assert command > 0


def test_altitude_hold_zero_error_gives_zero_command_initially() -> None:
    ap = AltitudeHoldAutopilot()
    command = ap.command(current_altitude=1000.0, target_altitude=1000.0, dt=0.1)
    assert command == 0.0


def test_altitude_hold_respects_elevator_limits() -> None:
    ap = AltitudeHoldAutopilot(kp=100.0, elevator_limits=(-0.2, 0.2))
    command = ap.command(current_altitude=0.0, target_altitude=10000.0, dt=0.1)
    assert command == -0.2


def test_heading_hold_turns_toward_target() -> None:
    ap = HeadingHoldAutopilot()
    command = ap.command(
        current_heading=math.radians(0), target_heading=math.radians(30), dt=0.1
    )
    assert command > 0


def test_heading_hold_handles_wraparound() -> None:
    """Heading hold should command a small turn across the 0/360 boundary, not
    a large one the long way around."""
    ap = HeadingHoldAutopilot()
    command = ap.command(
        current_heading=math.radians(350), target_heading=math.radians(10), dt=0.1
    )
    assert command > 0  # should turn right (positive) through 0/360, not left


def test_hold_autopilots_reset() -> None:
    ap = AltitudeHoldAutopilot()
    ap.command(current_altitude=900.0, target_altitude=1000.0, dt=0.1)
    ap.reset()
    assert ap._pid._integral == 0.0
