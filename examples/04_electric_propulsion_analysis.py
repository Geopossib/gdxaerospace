"""Example: Hall thruster performance, plume divergence, and spacecraft charging.

Run with:
    uv run python examples/04_electric_propulsion_analysis.py
"""

from __future__ import annotations

import math

from plasmathrust.constants import ION_MASS

from electricprop import HallThruster, IonThruster
from plasmaspace import floating_potential
from plasmathrust import (
    bohm_velocity,
    electron_cyclotron_frequency,
    hall_parameter,
    ion_cyclotron_frequency,
)
from plume3d import divergence_thrust_correction, effective_specific_impulse, effective_thrust


def thruster_comparison() -> None:
    """Compare an SPT-100-class Hall thruster against a NEXT-class ion thruster."""
    hall = HallThruster(voltage=300.0, current=4.5, mass_flow=5.0e-6)
    ion = IonThruster(voltage=1200.0, current=1.76, mass_flow=2.04e-6)

    print("=== Thruster comparison (ideal performance) ===")
    for name, thruster in (("Hall", hall), ("Ion", ion)):
        print(
            f"{name:>4}: F={thruster.thrust() * 1000:.1f} mN, "
            f"Isp={thruster.specific_impulse():.0f} s, "
            f"P={thruster.power():.0f} W, "
            f"eta={thruster.efficiency():.3f}"
        )

    half_angle = math.radians(25.0)
    corrected_thrust = effective_thrust(hall.thrust(), half_angle)
    corrected_isp = effective_specific_impulse(hall.specific_impulse(), half_angle)
    correction = divergence_thrust_correction(half_angle)
    print(
        f"\nHall thruster with {math.degrees(half_angle):.0f} deg divergence "
        f"(correction factor {correction:.3f}):"
    )
    print(f"  Effective thrust: {corrected_thrust * 1000:.1f} mN")
    print(f"  Effective Isp:    {corrected_isp:.0f} s")


def hall_thruster_magnetization() -> None:
    """Check the Hall parameter that makes a Hall thruster work.

    Magnetized electrons, unmagnetized ions.
    """
    magnetic_field = 0.015  # Tesla, typical Hall thruster discharge channel field
    electron_collision_freq = 1e7  # Hz, representative electron collision frequency

    omega_ce = electron_cyclotron_frequency(magnetic_field)
    omega_ci = ion_cyclotron_frequency(magnetic_field, ION_MASS["xenon"])
    beta_e = hall_parameter(omega_ce, electron_collision_freq)

    print("\n=== Hall thruster magnetization check ===")
    print(f"Electron cyclotron frequency: {omega_ce:.3e} rad/s")
    print(f"Xenon ion cyclotron frequency: {omega_ci:.3e} rad/s")
    print(f"Electron Hall parameter: {beta_e:.1f} (>>1 means well-magnetized)")


def spacecraft_charging_estimate() -> None:
    """Estimate the floating potential of a spacecraft surface.

    Uses a representative benign plasma environment.
    """
    electron_temp_ev = 1.0  # eV
    v_f_hydrogen = floating_potential(electron_temp_ev, ION_MASS["hydrogen"])
    u_bohm = bohm_velocity(electron_temp_ev, ION_MASS["hydrogen"])

    print("\n=== Spacecraft floating potential (idealized, no photoemission) ===")
    print(f"Bohm velocity (H+): {u_bohm:.1f} m/s")
    print(f"Floating potential: {v_f_hydrogen:.2f} V")


if __name__ == "__main__":
    thruster_comparison()
    hall_thruster_magnetization()
    spacecraft_charging_estimate()
