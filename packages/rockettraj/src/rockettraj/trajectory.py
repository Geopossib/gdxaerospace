"""Vertical rocket trajectory simulation: powered ascent, coast, and apogee.

Reference
---------
- Sutton, G.P. & Biblarz, O., *Rocket Propulsion Elements*, 9th ed.,
  Ch. 4 (the rocket equation of motion including gravity and drag
  losses, generalizing the ideal/vacuum rocket equation used
  elsewhere in this ecosystem's ``orbitpy``/``rocketperf`` packages).

Convention
----------
- 1D vertical motion only (altitude, positive up); no horizontal drift,
  wind, or launch-rail angle -- a straight-up trajectory.
- Constant thrust during the burn (a single-value thrust, not a
  time-varying thrust curve); propellant mass depletes linearly over
  the burn time.
- Drag opposes the direction of motion: ``F_drag = -sign(v) * 0.5 * rho
  * v^2 * Cd * A``, using :class:`aerocalc.Atmosphere` for
  altitude-varying air density (clamped to the model's valid
  0-86,000 m range).
- Gravity is treated as constant (``g0``) over the trajectory -- valid
  for sounding-rocket-scale altitudes, not for trajectories that reach
  a significant fraction of Earth's radius.

Assumptions
-----------
- No wind, no Earth rotation/Coriolis effects, no staging (single
  stage). Integration uses fixed-step RK4.
- Thrust and mass flow rate cut off discontinuously at ``burn_time``.
  Fixed-step RK4 evaluates intermediate stages that can straddle this
  discontinuity, producing a small (sub-0.1%, at typical step sizes)
  mass-conservation error right at burnout -- a known limitation of
  naive fixed-step integration across a discontinuous right-hand side,
  not a bug. Use a smaller ``dt`` if tighter mass conservation across
  burnout specifically matters for your use case.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from aerocalc.atmosphere import Atmosphere

from rockettraj.exceptions import InvalidTrajectoryInputError

#: Standard gravitational acceleration, m/s^2.
G0 = 9.80665
_MAX_ATMOSPHERE_ALTITUDE = 86_000.0


@dataclass(frozen=True)
class RocketConfig:
    """Configuration for a single-stage vertical rocket trajectory.

    Parameters
    ----------
    dry_mass:
        Rocket mass excluding propellant, kg, > 0.
    propellant_mass:
        Propellant mass, kg, > 0.
    burn_time:
        Motor burn duration, s, > 0.
    thrust:
        Constant thrust during the burn, N, > 0.
    drag_coefficient:
        Drag coefficient, dimensionless, > 0.
    reference_area:
        Reference area for drag, m^2, > 0.
    g0:
        Gravitational acceleration (assumed constant), m/s^2.

    """

    dry_mass: float
    propellant_mass: float
    burn_time: float
    thrust: float
    drag_coefficient: float
    reference_area: float
    g0: float = G0

    def __post_init__(self) -> None:
        for name in ("dry_mass", "propellant_mass", "burn_time", "thrust"):
            if getattr(self, name) <= 0:
                raise InvalidTrajectoryInputError(f"{name} must be positive")
        for name in ("drag_coefficient", "reference_area"):
            if getattr(self, name) <= 0:
                raise InvalidTrajectoryInputError(f"{name} must be positive")

    def mass_at(self, t: float) -> float:
        """Compute the instantaneous vehicle mass at time ``t``, kg."""
        if t >= self.burn_time:
            return self.dry_mass
        mass_flow_rate = self.propellant_mass / self.burn_time
        return self.dry_mass + self.propellant_mass - mass_flow_rate * t

    def thrust_at(self, t: float) -> float:
        """Compute the instantaneous thrust at time ``t``, N (zero after burnout)."""
        return self.thrust if t < self.burn_time else 0.0


@dataclass
class TrajectoryResult:
    """The recorded time history of a simulated trajectory."""

    times: list[float] = field(default_factory=list)
    altitudes: list[float] = field(default_factory=list)
    velocities: list[float] = field(default_factory=list)
    masses: list[float] = field(default_factory=list)

    @property
    def apogee_altitude(self) -> float:
        """Maximum altitude reached, m."""
        return max(self.altitudes)

    @property
    def apogee_time(self) -> float:
        """Time at which maximum altitude is reached, s."""
        return self.times[self.altitudes.index(self.apogee_altitude)]


def _air_density(altitude: float) -> float:
    clamped = min(max(altitude, 0.0), _MAX_ATMOSPHERE_ALTITUDE)
    return Atmosphere(clamped).density


def _derivative(
    state: tuple[float, float, float], t: float, config: RocketConfig
) -> tuple[float, float, float]:
    altitude, velocity, mass = state
    rho = _air_density(altitude)
    thrust = config.thrust_at(t)
    drag = 0.5 * rho * velocity * abs(velocity) * config.drag_coefficient * config.reference_area
    weight = mass * config.g0

    d_altitude = velocity
    d_velocity = (thrust - weight - drag) / mass
    d_mass = -config.propellant_mass / config.burn_time if t < config.burn_time else 0.0
    return d_altitude, d_velocity, d_mass


def _rk4_step(
    state: tuple[float, float, float], t: float, dt: float, config: RocketConfig
) -> tuple[float, float, float]:
    k1 = _derivative(state, t, config)
    s2 = tuple(s + dt / 2 * k for s, k in zip(state, k1, strict=True))
    k2 = _derivative(s2, t + dt / 2, config)
    s3 = tuple(s + dt / 2 * k for s, k in zip(state, k2, strict=True))
    k3 = _derivative(s3, t + dt / 2, config)
    s4 = tuple(s + dt * k for s, k in zip(state, k3, strict=True))
    k4 = _derivative(s4, t + dt, config)
    return tuple(
        s + (dt / 6) * (a + 2 * b + 2 * c + d)
        for s, a, b, c, d in zip(state, k1, k2, k3, k4, strict=True)
    )


def simulate_trajectory(
    config: RocketConfig, *, dt: float = 0.01, max_time: float = 1000.0
) -> TrajectoryResult:
    """Simulate a vertical launch from the ground through apogee to ground impact.

    Parameters
    ----------
    config:
        Rocket configuration.
    dt:
        Fixed integration time step, s, > 0.
    max_time:
        Safety cutoff on total simulated time, s, > 0 (in case the
        rocket never comes down, e.g. an unphysically low drag/mass
        configuration).

    Returns
    -------
    TrajectoryResult

    Example
    -------
    A small solid-motor sounding rocket:

    >>> config = RocketConfig(
    ...     dry_mass=5.0, propellant_mass=2.0, burn_time=3.0,
    ...     thrust=200.0, drag_coefficient=0.5, reference_area=0.01,
    ... )
    >>> result = simulate_trajectory(config)
    >>> result.apogee_altitude > 0
    True

    """
    if dt <= 0:
        raise InvalidTrajectoryInputError(f"dt must be positive, got {dt!r}")
    if max_time <= 0:
        raise InvalidTrajectoryInputError(f"max_time must be positive, got {max_time!r}")

    initial_mass = config.dry_mass + config.propellant_mass
    state = (0.0, 0.0, initial_mass)
    t = 0.0
    result = TrajectoryResult(
        times=[t], altitudes=[state[0]], velocities=[state[1]], masses=[state[2]]
    )

    while t < max_time:
        state = _rk4_step(state, t, dt, config)
        t += dt
        altitude, velocity, mass = state
        if altitude < 0.0 and t > config.burn_time:
            # Ground impact: stop, without recording the (unphysical) below-ground point.
            break
        result.times.append(t)
        result.altitudes.append(altitude)
        result.velocities.append(velocity)
        result.masses.append(mass)

    return result
