"""A discrete PID controller with clamping anti-windup.

Reference
---------
- Astrom, K.J. & Murray, R.M., *Feedback Systems: An Introduction for
  Scientists and Engineers*, 2nd ed., Ch. 11 (PID control, integrator
  windup and anti-windup).
- Franklin, G.F., Powell, J.D. & Emami-Naeini, A., *Feedback Control of
  Dynamic Systems*, 8th ed., Ch. 10, for the standard discrete PID form
  used here.

Assumptions
-----------
- Fixed, known ``dt`` per call (no variable-timestep compensation beyond
  what the caller provides).
- Anti-windup uses "conditional integration": when the unclamped output
  would saturate in the same direction the integral is currently pushing,
  the integral term is frozen rather than updated that step. This is one
  of several standard anti-windup schemes (compare "back-calculation");
  it is simple and effective for most flight-control-loop use cases.
- The derivative term acts on the raw error signal ("derivative on
  error"), not on the measured process variable ("derivative on
  measurement"). Derivative-on-error can produce a large transient
  ("derivative kick") on a step change in setpoint; callers doing
  setpoint tracking with step changes may prefer to filter or otherwise
  handle this externally.
"""

from __future__ import annotations

from autopilotpy.exceptions import InvalidControllerConfigError


class PIDController:
    """A standard discrete PID controller with output clamping and anti-windup.

    Parameters
    ----------
    kp, ki, kd:
        Proportional, integral, and derivative gains.
    output_limits:
        Optional ``(min, max)`` tuple to clamp the controller output.
        If ``None`` (default), output is unclamped and no anti-windup
        logic is applied (there is nothing to wind up against).

    """

    def __init__(
        self,
        kp: float,
        ki: float,
        kd: float,
        *,
        output_limits: tuple[float, float] | None = None,
    ) -> None:
        if output_limits is not None and output_limits[0] >= output_limits[1]:
            raise InvalidControllerConfigError(
                f"output_limits must satisfy min < max, got {output_limits!r}"
            )
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_limits = output_limits
        self._integral = 0.0
        self._prev_error: float | None = None

    def reset(self) -> None:
        """Reset the integral accumulator and derivative history."""
        self._integral = 0.0
        self._prev_error = None

    def update(self, error: float, dt: float) -> float:
        """Compute one controller output given the current error and time step.

        Parameters
        ----------
        error:
            Setpoint minus measured process variable (or any signal the
            controller should drive to zero).
        dt:
            Time since the last call, s, > 0.

        Returns
        -------
        float
            Controller output, clamped to ``output_limits`` if set.

        Example
        -------
        >>> pid = PIDController(kp=1.0, ki=0.0, kd=0.0)
        >>> pid.update(error=2.0, dt=0.1)
        2.0

        """
        if dt <= 0:
            raise InvalidControllerConfigError(f"dt must be positive, got {dt!r}")

        proportional = self.kp * error
        tentative_integral = self._integral + error * dt
        derivative = 0.0 if self._prev_error is None else (error - self._prev_error) / dt

        output = proportional + self.ki * tentative_integral + self.kd * derivative

        if self.output_limits is not None:
            lo, hi = self.output_limits
            if output > hi:
                output = hi
                if self.ki != 0 and error * self.ki > 0:
                    # Freeze: further integration would only worsen saturation.
                    tentative_integral = self._integral
            elif output < lo:
                output = lo
                if self.ki != 0 and error * self.ki < 0:
                    tentative_integral = self._integral

        self._integral = tentative_integral
        self._prev_error = error
        return output
