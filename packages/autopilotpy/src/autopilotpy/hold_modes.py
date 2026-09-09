"""Simple altitude-hold and heading-hold autopilot modes built on PIDController.

Reference
---------
- Nelson, R.C., *Flight Stability and Automatic Control*, 2nd ed., Ch. 10,
  for the altitude-hold and heading-hold autopilot loop structure (error
  -> PID -> control-surface command).

Assumptions
-----------
- Each hold mode is a single PID loop driving one control surface
  (elevator for altitude, aileron for heading/roll) -- a simplified,
  single-loop autopilot. Real autopilots typically cascade an inner
  attitude-stabilization loop with an outer altitude/heading loop; this
  module implements only the outer-loop concept directly for simplicity.
- Heading error correctly wraps around the 0/360-degree boundary (see
  :func:`heading_error`); altitude error does not need wrapping.
"""

from __future__ import annotations

import math

from autopilotpy.pid import PIDController


def heading_error(current_heading: float, target_heading: float) -> float:
    """Compute the shortest signed angular difference from current to target heading.

    Wraps correctly across the 0/2*pi boundary, e.g. going from 350 deg
    to 10 deg gives +20 deg, not -340 deg.

    Parameters
    ----------
    current_heading, target_heading:
        Headings, radians (any real value; not required to be pre-wrapped).

    Returns
    -------
    float
        Signed error in ``(-pi, pi]``, radians.

    Example
    -------
    >>> import math
    >>> round(math.degrees(heading_error(math.radians(350), math.radians(10))), 1)
    20.0

    """
    diff = (target_heading - current_heading + math.pi) % (2 * math.pi) - math.pi
    return diff


class AltitudeHoldAutopilot:
    """A single-loop altitude-hold autopilot: altitude error -> PID -> elevator command.

    Parameters
    ----------
    kp, ki, kd:
        PID gains for the altitude-error-to-elevator loop.
    elevator_limits:
        ``(min, max)`` elevator deflection, radians. Defaults to
        ``(-0.35, 0.35)`` (about +/-20 degrees).

    """

    def __init__(
        self,
        kp: float = 0.02,
        ki: float = 0.002,
        kd: float = 0.05,
        *,
        elevator_limits: tuple[float, float] = (-0.35, 0.35),
    ) -> None:
        self._pid = PIDController(kp, ki, kd, output_limits=elevator_limits)

    def reset(self) -> None:
        """Reset the internal PID controller state."""
        self._pid.reset()

    def command(self, current_altitude: float, target_altitude: float, dt: float) -> float:
        """Compute the elevator command to reduce altitude error.

        Parameters
        ----------
        current_altitude, target_altitude:
            Altitude, m.
        dt:
            Time since the last call, s, > 0.

        Returns
        -------
        float
            Elevator command, radians. Note the sign convention: this
            module's aero model uses ``Cm_elevator < 0`` (the standard
            aerospace convention, where positive/trailing-edge-down
            elevator produces a nose-DOWN moment), so climbing (current
            altitude below target) requires a NEGATIVE elevator command.
            This method uses ``error = current - target`` (not
            ``target - current``) so the sign works out correctly.

        """
        error = current_altitude - target_altitude
        return self._pid.update(error, dt)


class HeadingHoldAutopilot:
    """A single-loop heading-hold autopilot: heading error -> PID -> aileron command.

    Parameters
    ----------
    kp, ki, kd:
        PID gains for the heading-error-to-aileron loop.
    aileron_limits:
        ``(min, max)`` aileron deflection, radians. Defaults to
        ``(-0.35, 0.35)``.

    """

    def __init__(
        self,
        kp: float = 1.2,
        ki: float = 0.05,
        kd: float = 0.3,
        *,
        aileron_limits: tuple[float, float] = (-0.35, 0.35),
    ) -> None:
        self._pid = PIDController(kp, ki, kd, output_limits=aileron_limits)

    def reset(self) -> None:
        """Reset the internal PID controller state."""
        self._pid.reset()

    def command(self, current_heading: float, target_heading: float, dt: float) -> float:
        """Compute the aileron command to reduce (wrapped) heading error.

        Parameters
        ----------
        current_heading, target_heading:
            Heading, radians.
        dt:
            Time since the last call, s, > 0.

        Returns
        -------
        float
            Aileron command, radians.

        """
        error = heading_error(current_heading, target_heading)
        return self._pid.update(error, dt)
