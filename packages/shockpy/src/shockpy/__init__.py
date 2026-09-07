"""shockpy — normal shock, oblique shock, and Prandtl-Meyer expansion relations."""

from __future__ import annotations

from shockpy.exceptions import DetachedShockError
from shockpy.normal_shock import NormalShockResult, normal_shock
from shockpy.oblique_shock import ObliqueShockResult, oblique_shock, theta_from_beta
from shockpy.prandtl_meyer import (
    expansion_fan,
    mach_from_prandtl_meyer_angle,
    prandtl_meyer_angle,
)

__all__ = [
    "DetachedShockError",
    "NormalShockResult",
    "ObliqueShockResult",
    "expansion_fan",
    "mach_from_prandtl_meyer_angle",
    "normal_shock",
    "oblique_shock",
    "prandtl_meyer_angle",
    "theta_from_beta",
]

__version__ = "0.1.0"
