"""Exceptions for shockpy."""

from __future__ import annotations

import math

from aerocalc.exceptions import GDXAerospaceError


class DetachedShockError(GDXAerospaceError):
    """Raised when a requested deflection exceeds the max attached-shock angle.

    Beyond the maximum deflection angle for a given upstream Mach number, no
    attached oblique-shock solution exists; the shock detaches into a
    curved bow shock, which requires a different (non-algebraic) model not
    implemented in ``shockpy``.
    """

    def __init__(self, mach1: float, deflection: float, theta_max: float) -> None:
        message = (
            f"No attached oblique shock exists for M1={mach1:.3f} at a "
            f"deflection of {math.degrees(deflection):.2f} deg: the maximum "
            f"attached-shock deflection at this Mach number is "
            f"{math.degrees(theta_max):.2f} deg. The shock would detach into "
            "a curved bow shock, which shockpy does not model. Reduce the "
            "deflection angle or increase the upstream Mach number."
        )
        super().__init__(message)
        self.mach1 = mach1
        self.deflection = deflection
        self.theta_max = theta_max
