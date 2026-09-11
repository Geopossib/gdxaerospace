"""Thermal analysis, CFD case automation, and flight-data reduction demo.

Run with:
    uv run python examples/09_thermal_cfd_and_data.py
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from aerocfd import OpenFOAMCase, OpenFOAMNotFoundError, is_openfoam_available
from aerodata import descriptive_stats, detect_outliers_zscore, moving_average
from aerothermal import (
    lumped_capacitance_temperature,
    radiation_heat_transfer,
    spacecraft_equilibrium_temperature,
)


def thermal_demo() -> None:
    """Estimate a small spacecraft's radiative equilibrium and a cool-down transient."""
    print("=== Thermal analysis ===")
    t_eq = spacecraft_equilibrium_temperature(
        solar_flux=1361.0,
        absorptivity=0.2,
        emissivity=0.85,
        area_absorbing=1.0,
        area_emitting=4.0,
    )
    print(f"Spacecraft equilibrium temperature: {t_eq:.1f} K ({t_eq - 273.15:.1f} degC)")

    q_rad = radiation_heat_transfer(
        emissivity=0.85, area=4.0, hot_temperature=350.0, cold_temperature=t_eq
    )
    print(f"Radiative heat loss at 350 K: {q_rad:.1f} W")

    cooldown = lumped_capacitance_temperature(
        initial_temperature=350.0,
        ambient_temperature=t_eq,
        convection_coefficient=5.0,
        area=4.0,
        density=2700.0,
        volume=0.01,
        specific_heat=900.0,
        time=3600.0,
    )
    print(f"Temperature after 1 hour of convective cooling: {cooldown:.1f} K")


def cfd_demo() -> None:
    """Generate an OpenFOAM case and demonstrate the not-installed error path."""
    print("\n=== CFD case automation ===")
    with tempfile.TemporaryDirectory() as tmp:
        case = OpenFOAMCase("naca0012_5deg", base_dir=Path(tmp))
        case.set_velocity(50.0)
        case.set_angle_of_attack(5.0)
        case.set_turbulence_model("kOmegaSST")
        case.generate()

        files = sorted(
            p.relative_to(case.case_dir) for p in case.case_dir.rglob("*") if p.is_file()
        )
        print(f"Generated case files: {[str(f) for f in files]}")

        print(f"OpenFOAM available on this system: {is_openfoam_available()}")
        try:
            case.run()
        except OpenFOAMNotFoundError as exc:
            print("As expected without OpenFOAM installed: " + str(exc)[:100] + "...")


def flight_data_demo() -> None:
    """Smooth noisy simulated altitude data and flag an injected sensor glitch."""
    print("\n=== Flight-test data reduction ===")
    rng = np.random.default_rng(7)
    t = np.arange(0, 60, 1.0)
    true_altitude = 1000.0 + 5.0 * t
    noisy_altitude = true_altitude + rng.normal(0, 3.0, size=len(t))
    noisy_altitude[40] += 80.0  # simulated glitch

    df = pd.DataFrame({"t": t, "altitude": noisy_altitude})
    smoothed = moving_average(df["altitude"], window=5)

    # Outlier detection works on a stationary signal, not one with a strong trend
    # (a linear climb inflates the overall std and can mask a glitch) -- detrend
    # against the smoothed series first, a standard practice before z-score screening.
    residual = df["altitude"] - smoothed
    outliers = detect_outliers_zscore(residual, threshold=3.0)

    stats = descriptive_stats(df["altitude"])
    print(f"Raw altitude stats: mean={stats.mean:.1f} m, std={stats.std:.2f} m")
    print(f"Flagged {outliers.sum()} outlier(s) at t={df['t'][outliers].tolist()}")
    print(
        f"Smoothed altitude at t=45s: {smoothed.iloc[45]:.1f} m "
        f"(raw: {df['altitude'].iloc[45]:.1f} m)"
    )


if __name__ == "__main__":
    thermal_demo()
    cfd_demo()
    flight_data_demo()
