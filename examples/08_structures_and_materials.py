"""Structures and materials demo: a metallic spar and a composite panel.

Run with:
    uv run python examples/08_structures_and_materials.py
"""

from __future__ import annotations

import math

from aeromaterials import get_material
from aerostruct import i_beam_properties
from bucklingpy import K_FIXED_FREE, euler_buckling_load
from compositepy import LaminaStrengths, max_stress_margins, reduced_stiffness
from fatiguepy import basquin_life, miners_rule_damage
from laminatepy import Ply, compute_abd, laminate_response
from sparcalc import cantilever_tip_deflection_point_load
from stresspy import bending_stress


def metallic_spar_demo() -> None:
    """Size a simple I-beam wing spar in Al 7075-T6.

    Checks bending, deflection, buckling, and fatigue.
    """
    print("=== Metallic spar: Al 7075-T6 I-beam ===")
    material = get_material("Al7075-T6")
    section = i_beam_properties(
        flange_width=0.06, flange_thickness=0.008, web_height=0.08, web_thickness=0.005
    )
    span = 1.5  # m, half-span cantilever segment
    tip_load = 4000.0  # N

    deflection = cantilever_tip_deflection_point_load(
        tip_load, span, material.youngs_modulus, section.ixx
    )
    max_bending_stress = bending_stress(
        moment=tip_load * span, distance_from_neutral_axis=0.048, moment_of_inertia=section.ixx
    )
    margin = material.yield_strength / max_bending_stress - 1

    buckling_load = euler_buckling_load(
        material.youngs_modulus, section.iyy, span, k_factor=K_FIXED_FREE
    )

    print(f"Section area: {section.area * 1e4:.2f} cm^2, Ixx: {section.ixx * 1e8:.2f} cm^4")
    print(f"Tip deflection under {tip_load:.0f} N: {deflection * 1000:.2f} mm")
    print(f"Max bending stress: {max_bending_stress / 1e6:.1f} MPa (margin: {margin:.2f})")
    print(f"Euler buckling load (weak axis, cantilever): {buckling_load / 1000:.1f} kN")

    print("\n--- Fatigue check ---")
    stress_amplitude = 150e6
    fatigue_life = basquin_life(
        stress_amplitude, fatigue_strength_coefficient=1200e6, fatigue_strength_exponent=-0.12
    )
    damage = miners_rule_damage(cycles_applied=[50_000.0], cycles_to_failure=[fatigue_life])
    print(f"Predicted life at {stress_amplitude / 1e6:.0f} MPa: {fatigue_life:,.0f} cycles")
    print(f"Miner's damage after 50,000 applied cycles: {damage:.3f}")


def composite_panel_demo() -> None:
    """Analyze a symmetric [0/90/90/0] T300/5208 laminate panel."""
    print("\n=== Composite panel: T300/5208 [0/90/90/0] laminate ===")
    q = reduced_stiffness(e1=181e9, e2=10.3e9, nu12=0.28, g12=7.17e9)
    ply_thickness = 0.000125  # 0.125 mm per ply, typical prepreg tape
    plies = [
        Ply(ply_thickness, math.radians(0), q),
        Ply(ply_thickness, math.radians(90), q),
        Ply(ply_thickness, math.radians(90), q),
        Ply(ply_thickness, math.radians(0), q),
    ]
    abd = compute_abd(plies)
    print(f"Laminate thickness: {sum(p.thickness for p in plies) * 1000:.3f} mm")
    print(f"Coupling stiffness B (should be ~0, symmetric layup): max|B|={abs(abd.b).max():.2e}")

    n_applied = [2e5, 0.0, 0.0]  # N/m, uniaxial in-plane load
    eps0, kappa = laminate_response(abd, n_applied, [0.0, 0.0, 0.0])
    print(f"Mid-plane strain under {n_applied[0] / 1000:.0f} kN/m: eps_x={eps0[0]:.5f}")

    strengths = LaminaStrengths(
        x_tension=1500e6, x_compression=1500e6, y_tension=40e6, y_compression=246e6, s=68e6
    )
    # Approximate ply-level stress in the 0-degree plies from the applied strain.
    sigma_1 = q.q11 * eps0[0]
    margins = max_stress_margins(sigma_1, 0.0, 0.0, strengths)
    print(f"0-deg ply fiber-direction stress: {sigma_1 / 1e6:.1f} MPa")
    print(f"Fiber-direction margin of safety: {margins['fiber']:.2f}")


if __name__ == "__main__":
    metallic_spar_demo()
    composite_panel_demo()
