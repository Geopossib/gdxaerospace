"""A simple 6-DOF aircraft flight simulator.

Combines flightdyn, attitude3d, and a generic linear aerodynamic model,
integrated with fixed-step RK4.

Reference
---------
- See :mod:`flightdyn.rigid_body` for the equations of motion and
  :mod:`aircraftsim.aero_model` for the aerodynamic model, each with
  their own citations and stated assumptions.
- RK4 (classical 4th-order Runge-Kutta) is the standard fixed-step
  integrator for this kind of nonlinear 6-DOF simulation (Stevens &
  Lewis, *Aircraft Control and Simulation*, 3rd ed., Ch. 1).

Assumptions
-----------
- Flat, non-rotating Earth (NED inertial frame): ``position = [north,
  east, down]``, so altitude ``= -position[2]``.
- Thrust is a simplified constant-static-thrust model,
  ``T = throttle * max_thrust``, acting along the body +X axis. This
  ignores propeller efficiency, advance ratio, and altitude/density
  effects on thrust -- a first-order approximation only.
- The quaternion is renormalized after every integration step to control
  numerical drift (see :func:`attitude3d.quaternion_normalize`).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from aerocalc.atmosphere import Atmosphere
from aerocalc.flow import dynamic_pressure
from attitude3d.rotations import (
    quaternion_derivative,
    quaternion_normalize,
    quaternion_to_dcm,
    quaternion_to_euler,
)
from flightdyn.rigid_body import (
    G0,
    gravity_body_frame,
    position_derivative,
    rotational_acceleration,
    translational_acceleration,
)

from aircraftsim.aero_model import LinearAeroModel
from aircraftsim.exceptions import InvalidAircraftConfigError

#: Minimum airspeed, m/s, below which alpha/beta are treated as zero to avoid
#: division by (near-)zero in their definitions.
_MIN_AIRSPEED = 1e-6


@dataclass
class Aircraft6DOF:
    """A simple 6-DOF rigid-body aircraft simulator.

    Parameters
    ----------
    mass:
        Aircraft mass, kg, > 0.
    inertia:
        Principal moments of inertia ``(Ixx, Iyy, Izz)``, kg*m^2, each > 0
        (no products of inertia -- assumes mass symmetry about the
        X-Z plane, standard for most fixed-wing aircraft).
    wing_area:
        Reference wing area, m^2, > 0.
    wingspan:
        Wingspan, m, > 0. Defaults to 11.0 m (a small general-aviation
        aircraft scale) if not given.
    mean_chord:
        Mean aerodynamic chord, m, > 0. Defaults to ``wing_area / wingspan``.
    aero:
        Aerodynamic model. Defaults to :class:`aircraftsim.aero_model.LinearAeroModel`
        with generic illustrative coefficients (see its docstring).
    max_thrust:
        Maximum (full-throttle) thrust, N, > 0. Defaults to 2500 N.
    initial_altitude:
        Initial altitude, m (>= 0), default 1000.0.
    initial_airspeed:
        Initial body-axis forward airspeed, m/s, default 60.0.

    """

    mass: float
    inertia: tuple[float, float, float]
    wing_area: float
    wingspan: float | None = None
    mean_chord: float | None = None
    aero: LinearAeroModel = field(default_factory=LinearAeroModel)
    max_thrust: float = 2500.0
    initial_altitude: float = 1000.0
    initial_airspeed: float = 60.0

    def __post_init__(self) -> None:
        if self.mass <= 0:
            raise InvalidAircraftConfigError(f"mass must be positive, got {self.mass!r}")
        if any(i <= 0 for i in self.inertia):
            raise InvalidAircraftConfigError(
                f"all inertia components must be positive, got {self.inertia!r}"
            )
        if self.wing_area <= 0:
            raise InvalidAircraftConfigError(f"wing_area must be positive, got {self.wing_area!r}")
        if self.wingspan is None:
            self.wingspan = 11.0
        if self.mean_chord is None:
            self.mean_chord = self.wing_area / self.wingspan
        if self.max_thrust <= 0:
            raise InvalidAircraftConfigError(
                f"max_thrust must be positive, got {self.max_thrust!r}"
            )
        if self.initial_altitude < 0:
            raise InvalidAircraftConfigError(
                f"initial_altitude must be non-negative, got {self.initial_altitude!r}"
            )

        self._inertia_arr = np.array(self.inertia, dtype=float)
        # State vector: [north, east, down, u, v, w, q0, q1, q2, q3, p, q, r]
        self._state = np.zeros(13)
        self._state[2] = -self.initial_altitude
        self._state[3] = self.initial_airspeed
        self._state[6] = 1.0  # q0 = 1 (identity attitude)

    def _aero_and_forces(
        self, state: np.ndarray, controls: dict[str, float]
    ) -> tuple[np.ndarray, np.ndarray]:
        velocity_body = state[3:6]
        quat = state[6:10]
        altitude = max(0.0, min(86_000.0, -state[2]))

        airspeed = float(np.linalg.norm(velocity_body))
        if airspeed < _MIN_AIRSPEED:
            alpha, beta = 0.0, 0.0
        else:
            alpha = math.atan2(velocity_body[2], velocity_body[0])
            beta = math.asin(min(1.0, max(-1.0, velocity_body[1] / airspeed)))

        atm = Atmosphere(altitude)
        qbar = dynamic_pressure(atm.density, airspeed) if airspeed > 0 else 0.0

        elevator = controls.get("elevator", 0.0)
        aileron = controls.get("aileron", 0.0)
        rudder = controls.get("rudder", 0.0)
        throttle = min(1.0, max(0.0, controls.get("throttle", 0.0)))

        cl = self.aero.lift_coefficient(alpha)
        cd = self.aero.drag_coefficient(cl)
        cm = self.aero.pitching_moment_coefficient(alpha, elevator)
        cy = self.aero.side_force_coefficient(beta)
        c_roll = self.aero.rolling_moment_coefficient(beta, aileron)
        c_yaw = self.aero.yawing_moment_coefficient(beta, rudder)

        lift = qbar * self.wing_area * cl
        drag = qbar * self.wing_area * cd
        side_force = qbar * self.wing_area * cy

        x_aero = lift * math.sin(alpha) - drag * math.cos(alpha)
        z_aero = -lift * math.cos(alpha) - drag * math.sin(alpha)
        thrust = throttle * self.max_thrust

        force_body = np.array([x_aero + thrust, side_force, z_aero])
        dcm = quaternion_to_dcm(quat)
        force_body = force_body + self.mass * gravity_body_frame(dcm, g0=G0)

        # wingspan/mean_chord are resolved from None to floats in __post_init__;
        # re-assert here so the type checker can see that invariant too.
        assert self.wingspan is not None
        assert self.mean_chord is not None
        moment_body = np.array(
            [
                qbar * self.wing_area * self.wingspan * c_roll,
                qbar * self.wing_area * self.mean_chord * cm,
                qbar * self.wing_area * self.wingspan * c_yaw,
            ]
        )
        return force_body, moment_body

    def _state_derivative(self, state: np.ndarray, controls: dict[str, float]) -> np.ndarray:
        velocity_body = state[3:6]
        quat = state[6:10]
        omega = state[10:13]

        force_body, moment_body = self._aero_and_forces(state, controls)
        dcm = quaternion_to_dcm(quat)

        d_position = position_derivative(dcm, velocity_body)
        d_velocity = translational_acceleration(velocity_body, omega, force_body, self.mass)
        d_quat = quaternion_derivative(quat, omega)
        d_omega = rotational_acceleration(omega, moment_body, self._inertia_arr)

        derivative = np.zeros(13)
        derivative[0:3] = d_position
        derivative[3:6] = d_velocity
        derivative[6:10] = d_quat
        derivative[10:13] = d_omega
        return derivative

    def step(self, dt: float, controls: dict[str, float] | None = None) -> dict[str, Any]:
        """Advance the simulation by ``dt`` seconds using fixed-step RK4.

        Parameters
        ----------
        dt:
            Integration time step, s, > 0.
        controls:
            Dict with optional keys ``"elevator"``, ``"aileron"``,
            ``"rudder"`` (radians) and ``"throttle"`` (0-1, clamped).
            Missing keys default to 0.

        Returns
        -------
        dict
            A snapshot of the post-step state: ``altitude`` (m),
            ``north``, ``east`` (m), ``airspeed`` (m/s), ``alpha``,
            ``beta`` (rad), ``roll``, ``pitch``, ``yaw`` (rad),
            ``p``, ``q``, ``r`` (rad/s).

        """
        if dt <= 0:
            raise InvalidAircraftConfigError(f"dt must be positive, got {dt!r}")
        controls = controls or {}

        s = self._state
        k1 = self._state_derivative(s, controls)
        k2 = self._state_derivative(s + 0.5 * dt * k1, controls)
        k3 = self._state_derivative(s + 0.5 * dt * k2, controls)
        k4 = self._state_derivative(s + dt * k3, controls)
        s_new = s + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        s_new[6:10] = quaternion_normalize(s_new[6:10])
        self._state = s_new

        return self.state_snapshot()

    def state_snapshot(self) -> dict[str, Any]:
        """Return a human-readable snapshot of the current state."""
        s = self._state
        velocity_body = s[3:6]
        quat = s[6:10]
        omega = s[10:13]
        roll, pitch, yaw = quaternion_to_euler(quat)
        airspeed = float(np.linalg.norm(velocity_body))
        if airspeed < _MIN_AIRSPEED:
            alpha, beta = 0.0, 0.0
        else:
            alpha = math.atan2(velocity_body[2], velocity_body[0])
            beta = math.asin(min(1.0, max(-1.0, velocity_body[1] / airspeed)))
        return {
            "north": float(s[0]),
            "east": float(s[1]),
            "altitude": float(-s[2]),
            "airspeed": airspeed,
            "alpha": alpha,
            "beta": beta,
            "roll": roll,
            "pitch": pitch,
            "yaw": yaw,
            "p": float(omega[0]),
            "q": float(omega[1]),
            "r": float(omega[2]),
        }
