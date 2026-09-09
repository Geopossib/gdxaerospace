"""A generic linear (stability-derivative) aerodynamic model for a small aircraft.

Reference
---------
- Roskam, J., *Airplane Flight Dynamics and Automatic Flight Controls*,
  Part I, Ch. 5-7, for the general form of a linear stability-derivative
  aerodynamic model and typical magnitude ranges for general-aviation
  aircraft.
- Etkin, B. & Reid, L.D., *Dynamics of Flight: Stability and Control*,
  3rd ed., Ch. 4, for the wind-to-body force resolution.

Assumptions
-----------
- Small-sideslip, decoupled model: lift and drag depend only on angle of
  attack (alpha) and are resolved into the body X-Z plane by a rotation
  through alpha alone; sideslip (beta) affects only side force and the
  lateral-directional moments. This decoupling is a standard
  simplification (Etkin) valid for small beta; it is NOT a full 3D
  wind-axes transform.
- All derivatives are linear (constant slopes) -- no stall, no
  compressibility, no control-surface rate limits.
- **The default coefficient values are illustrative, generic
  general-aviation-class magnitudes only** (loosely informed by the
  typical ranges tabulated in Roskam) -- they are NOT validated flight
  data for any specific aircraft type. Replace them with real derivatives
  (from wind-tunnel data, CFD, or flight test) for any application beyond
  demonstration and teaching.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LinearAeroModel:
    """Linear stability-derivative aerodynamic model coefficients.

    All coefficients are dimensionless stability derivatives; angles and
    control deflections are in radians.
    """

    cl0: float = 0.25
    cl_alpha: float = 5.5
    cd0: float = 0.028
    induced_drag_factor: float = 0.045
    cm0: float = 0.02
    cm_alpha: float = -1.1
    cm_elevator: float = -1.3
    cy_beta: float = -0.7
    cl_beta: float = -0.09
    cl_aileron: float = 0.17
    cn_beta: float = 0.10
    cn_rudder: float = -0.09

    def lift_coefficient(self, alpha: float) -> float:
        """Lift coefficient: ``CL = CL0 + CL_alpha * alpha``."""
        return self.cl0 + self.cl_alpha * alpha

    def drag_coefficient(self, cl: float) -> float:
        """Drag coefficient (parabolic polar): ``CD = CD0 + k * CL^2``."""
        return self.cd0 + self.induced_drag_factor * cl**2

    def pitching_moment_coefficient(self, alpha: float, elevator: float) -> float:
        """Pitching moment coefficient: ``Cm = Cm0 + Cm_alpha*alpha + Cm_elevator*elevator``."""
        return self.cm0 + self.cm_alpha * alpha + self.cm_elevator * elevator

    def side_force_coefficient(self, beta: float) -> float:
        """Side-force coefficient: ``Cy = Cy_beta * beta``."""
        return self.cy_beta * beta

    def rolling_moment_coefficient(self, beta: float, aileron: float) -> float:
        """Rolling-moment coefficient: ``Cl = Cl_beta*beta + Cl_aileron*aileron``."""
        return self.cl_beta * beta + self.cl_aileron * aileron

    def yawing_moment_coefficient(self, beta: float, rudder: float) -> float:
        """Yawing-moment coefficient: ``Cn = Cn_beta*beta + Cn_rudder*rudder``."""
        return self.cn_beta * beta + self.cn_rudder * rudder
