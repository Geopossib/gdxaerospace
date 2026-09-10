"""orbitpy — two-body Keplerian orbital mechanics for GDX Aerospace."""

from __future__ import annotations

from orbitpy.constants import EARTH_MU, EARTH_RADIUS, EARTH_ROTATION_RATE
from orbitpy.elements import cartesian_to_kepler, kepler_to_cartesian
from orbitpy.exceptions import InvalidOrbitError, OrbitSolverConvergenceError
from orbitpy.kepler import (
    circular_velocity,
    eccentric_anomaly_from_true,
    escape_velocity,
    orbital_period,
    solve_kepler_equation,
    true_anomaly_from_eccentric,
    vis_viva_speed,
)
from orbitpy.maneuvers import (
    BiellipticTransferResult,
    HohmannTransferResult,
    bielliptic_transfer,
    combined_plane_change_delta_v,
    hohmann_transfer,
    inclination_change_delta_v,
)

__all__ = [
    "EARTH_MU",
    "EARTH_RADIUS",
    "EARTH_ROTATION_RATE",
    "BiellipticTransferResult",
    "HohmannTransferResult",
    "InvalidOrbitError",
    "OrbitSolverConvergenceError",
    "bielliptic_transfer",
    "cartesian_to_kepler",
    "circular_velocity",
    "combined_plane_change_delta_v",
    "eccentric_anomaly_from_true",
    "escape_velocity",
    "hohmann_transfer",
    "inclination_change_delta_v",
    "kepler_to_cartesian",
    "orbital_period",
    "solve_kepler_equation",
    "true_anomaly_from_eccentric",
    "vis_viva_speed",
]

__version__ = "0.1.0"
