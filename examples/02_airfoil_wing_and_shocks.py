"""Example: airfoil geometry, finite-wing corrections, and shock relations.

Models a simple straight wing built from a NACA 2412 section, then analyzes
a separate supersonic-inlet-style oblique shock/expansion pair.

Run with:
    uv run python examples/02_airfoil_wing_and_shocks.py
"""

from __future__ import annotations

import math

from airfoilpy import naca4_coordinates
from shockpy import expansion_fan, normal_shock, oblique_shock
from wingtools import (
    finite_wing_lift_curve_slope,
    induced_drag_coefficient,
    oswald_efficiency_estimate,
)


def wing_analysis() -> None:
    """Compute finite-wing lift-curve slope and induced drag for a NACA 2412 wing."""
    coords = naca4_coordinates("2412", n_points=200)
    print(
        f"NACA 2412 max upper-surface ordinate: {coords.y_upper.max():.4f} "
        "(fraction of chord)"
    )

    aspect_ratio = 8.0
    a0 = 2 * math.pi  # thin-airfoil-theory 2D lift-curve slope, per radian
    a3d = finite_wing_lift_curve_slope(a0, aspect_ratio)
    e = oswald_efficiency_estimate(aspect_ratio)
    cl = 0.5
    cdi = induced_drag_coefficient(cl, aspect_ratio, oswald_efficiency=e)

    print(f"3D lift-curve slope (AR={aspect_ratio}): {a3d:.3f} /rad (2D: {a0:.3f} /rad)")
    print(f"Oswald efficiency estimate: {e:.3f}")
    print(f"Induced drag at CL={cl}: {cdi:.5f}")


def shock_analysis() -> None:
    """Run an oblique-shock, normal-shock, and expansion-fan analysis at M1=2.2."""
    mach1 = 2.2
    deflection = math.radians(12.0)

    shock = oblique_shock(mach1, deflection)
    print(
        f"Oblique shock: M1={mach1}, deflection={math.degrees(deflection):.1f} deg -> "
        f"beta={math.degrees(shock.shock_angle):.2f} deg, M2={shock.mach_downstream:.3f}, "
        f"p2/p1={shock.pressure_ratio:.3f}"
    )

    normal = normal_shock(shock.mach_downstream if shock.mach_downstream > 1 else mach1)
    print(f"Normal shock at M1={normal.mach_upstream}: M2={normal.mach_downstream:.4f}")

    mach2, p0_ratio = expansion_fan(mach1, deflection)
    print(
        f"Prandtl-Meyer expansion: M1={mach1}, turn={math.degrees(deflection):.1f} deg -> "
        f"M2={mach2:.3f}, p02/p01={p0_ratio}"
    )


if __name__ == "__main__":
    wing_analysis()
    print()
    shock_analysis()
