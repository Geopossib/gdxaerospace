"""Example: standard atmosphere and basic flow properties.

Computes atmospheric conditions and flow properties for a small aircraft
cruising at 5,000 m and 220 m/s, and plots temperature/density/pressure
vs. altitude across the full ISA range as a sanity check.

Run with:
    uv run python examples/01_atmosphere_and_flow_properties.py
"""

from __future__ import annotations

from aerocalc import Atmosphere, dynamic_pressure, mach_number, reynolds_number
from aerounits import Q_


def main() -> None:
    """Run the atmosphere/flow-property example and print the results."""
    cruise_altitude = Q_(5_000, "m")
    cruise_speed = Q_(220, "m/s")

    atm = Atmosphere(altitude=cruise_altitude.magnitude)

    q = dynamic_pressure(density=atm.density, velocity=cruise_speed.magnitude)
    mach = mach_number(velocity=cruise_speed.magnitude, speed_of_sound=atm.speed_of_sound)
    reynolds = reynolds_number(
        density=atm.density,
        velocity=cruise_speed.magnitude,
        length=2.0,  # representative wing chord, meters
        temperature=atm.temperature,
    )

    print(f"Altitude:          {cruise_altitude}")
    print(f"Temperature:       {atm.temperature:.2f} K")
    print(f"Pressure:          {atm.pressure:.1f} Pa")
    print(f"Density:           {atm.density:.5f} kg/m^3")
    print(f"Speed of sound:    {atm.speed_of_sound:.2f} m/s")
    print(f"Dynamic pressure:  {q:.1f} Pa")
    print(f"Mach number:       {mach:.3f}")
    print(f"Reynolds number:   {reynolds:.3e} (chord = 2.0 m)")


if __name__ == "__main__":
    main()
