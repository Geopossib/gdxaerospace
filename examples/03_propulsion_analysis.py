"""Example: rocket engine performance and a simple turbojet cycle.

Run with:
    uv run python examples/03_propulsion_analysis.py
"""

from __future__ import annotations

from combustionpy import stoichiometric_air_fuel_ratio, temperature_rise_estimate
from nozzleanalysis import choked_mass_flow, exit_mach_from_area_ratio, nozzle_exit_conditions
from rocketperf import (
    characteristic_velocity,
    effective_exhaust_velocity,
    ideal_delta_v,
    specific_impulse_rocket,
    thrust_coefficient,
)
from turbomachpy import compressor_temperature_rise, specific_work, turbine_temperature_drop


def rocket_engine_analysis() -> None:
    """Analyze a small liquid rocket engine from chamber conditions to Isp."""
    chamber_pressure = 7e6  # Pa
    chamber_temperature = 3500.0  # K
    throat_area = 0.01  # m^2
    exit_area_ratio = 8.0
    gamma = 1.22
    gas_constant = 380.0  # J/(kg*K), typical for hot rocket combustion gas

    mdot = choked_mass_flow(
        chamber_pressure, chamber_temperature, throat_area,
        gamma=gamma, specific_gas_constant=gas_constant,
    )
    exit_mach = exit_mach_from_area_ratio(exit_area_ratio, gamma=gamma)
    exit_temp, exit_velocity = nozzle_exit_conditions(
        chamber_temperature, exit_mach, gamma=gamma, specific_gas_constant=gas_constant
    )

    thrust = mdot * exit_velocity  # perfectly-expanded approximation (pe = pa)
    c = effective_exhaust_velocity(thrust, mdot)
    isp = specific_impulse_rocket(c)
    c_star = characteristic_velocity(chamber_pressure, throat_area, mdot)
    cf = thrust_coefficient(thrust, chamber_pressure, throat_area)
    dv = ideal_delta_v(c, mass_initial=1000.0, mass_final=400.0)

    print("=== Rocket engine ===")
    print(f"Mass flow:        {mdot:.2f} kg/s")
    print(f"Exit Mach:        {exit_mach:.2f}")
    print(f"Exit T, V:        {exit_temp:.1f} K, {exit_velocity:.1f} m/s")
    print(f"Thrust:           {thrust:.1f} N")
    print(f"Isp:              {isp:.1f} s")
    print(f"c*:               {c_star:.1f} m/s")
    print(f"CF:               {cf:.3f}")
    print(f"Ideal dv (1000->400 kg): {dv:.1f} m/s")


def turbojet_cycle_analysis() -> None:
    """Analyze a simple single-spool turbojet Brayton cycle at design point."""
    inlet_temp = 288.0  # K, ISA sea level
    pressure_ratio = 10.0
    compressor_eta = 0.85
    turbine_inlet_temp = 1400.0  # K
    turbine_eta = 0.90
    cp_cold, cp_hot = 1005.0, 1148.0

    compressor_dt = compressor_temperature_rise(inlet_temp, pressure_ratio, compressor_eta)
    compressor_work = specific_work(cp_cold, compressor_dt)

    turbine_dt = turbine_temperature_drop(turbine_inlet_temp, pressure_ratio, turbine_eta)
    turbine_work = specific_work(cp_hot, turbine_dt)

    fuel_flow, air_flow, lhv = 1.0, 50.0, 43e6
    combustor_dt = temperature_rise_estimate(fuel_flow, air_flow, lhv)
    afr_stoich = stoichiometric_air_fuel_ratio(carbon=12, hydrogen=23)  # kerosene surrogate

    print("\n=== Turbojet cycle ===")
    print(f"Compressor delivery temp: {inlet_temp + compressor_dt:.1f} K")
    print(f"Compressor specific work: {compressor_work / 1000:.1f} kJ/kg")
    print(f"Turbine exit temp:        {turbine_inlet_temp - turbine_dt:.1f} K")
    print(f"Turbine specific work:    {turbine_work / 1000:.1f} kJ/kg")
    print(f"Net specific work:        {(turbine_work - compressor_work) / 1000:.1f} kJ/kg")
    print(f"Combustor dT estimate:    {combustor_dt:.1f} K (simplified constant-cp)")
    print(f"Kerosene stoichiometric AFR: {afr_stoich:.2f}")


if __name__ == "__main__":
    rocket_engine_analysis()
    turbojet_cycle_analysis()
