"""Lumped-capacitance transient response and spacecraft radiative equilibrium.

Reference
---------
- Incropera, F.P. & DeWitt, D.P., *Fundamentals of Heat and Mass
  Transfer*, 6th ed., Ch. 5 (lumped capacitance method, valid when the
  Biot number ``Bi = h*Lc/k << 1``, i.e. internal conduction resistance
  is negligible compared to surface convection resistance).
- Wertz, J.R. & Larson, W.J. (eds.), *Space Mission Analysis and
  Design* (SMAD), 3rd ed., Ch. 11, for the simple radiative-balance
  spacecraft equilibrium temperature model used here.

Assumptions
-----------
- ``lumped_capacitance_temperature`` assumes negligible internal
  temperature gradients within the body (the lumped-capacitance
  approximation) -- valid only for small, high-conductivity, or
  thin-walled objects; this module does not check the Biot number for
  the caller.
- ``spacecraft_equilibrium_temperature`` is a simple radiative-balance
  model: absorbed solar power equals emitted thermal-IR power, with no
  internal heat generation, albedo/Earth-IR environmental loads, or
  transient effects (orbit eclipse, spin-averaging) -- a first-order
  mission-design estimate, not a substitute for a full thermal model.
"""

from __future__ import annotations

import math

from aerothermal.exceptions import InvalidThermalInputError
from aerothermal.heat_transfer import STEFAN_BOLTZMANN_CONSTANT


def lumped_capacitance_temperature(
    initial_temperature: float,
    ambient_temperature: float,
    convection_coefficient: float,
    area: float,
    density: float,
    volume: float,
    specific_heat: float,
    time: float,
) -> float:
    """Compute the temperature of a lumped-capacitance body relaxing toward ambient.

    ``(T(t) - T_inf) / (T_i - T_inf) = exp(-h*A*t / (rho*V*c))``.

    Parameters
    ----------
    initial_temperature:
        Initial body temperature, K.
    ambient_temperature:
        Ambient (surrounding fluid) temperature, K.
    convection_coefficient:
        Convective heat transfer coefficient, W/(m^2*K), > 0.
    area:
        Body surface area, m^2, > 0.
    density:
        Body material density, kg/m^3, > 0.
    volume:
        Body volume, m^3, > 0.
    specific_heat:
        Body material specific heat, J/(kg*K), > 0.
    time:
        Elapsed time, s, >= 0.

    Returns
    -------
    float
        Body temperature at time ``t``, K.

    Example
    -------
    >>> round(
    ...     lumped_capacitance_temperature(
    ...         initial_temperature=400.0, ambient_temperature=300.0,
    ...         convection_coefficient=25.0, area=0.1, density=2700.0,
    ...         volume=0.001, specific_heat=900.0, time=60.0,
    ...     ),
    ...     2,
    ... )
    394.01

    """
    if convection_coefficient <= 0:
        raise InvalidThermalInputError(
            f"convection_coefficient must be positive, got {convection_coefficient!r}"
        )
    if area <= 0:
        raise InvalidThermalInputError(f"area must be positive, got {area!r}")
    if density <= 0:
        raise InvalidThermalInputError(f"density must be positive, got {density!r}")
    if volume <= 0:
        raise InvalidThermalInputError(f"volume must be positive, got {volume!r}")
    if specific_heat <= 0:
        raise InvalidThermalInputError(f"specific_heat must be positive, got {specific_heat!r}")
    if time < 0:
        raise InvalidThermalInputError(f"time must be non-negative, got {time!r}")

    thermal_mass = density * volume * specific_heat
    time_constant = thermal_mass / (convection_coefficient * area)
    fraction_remaining = math.exp(-time / time_constant)
    return ambient_temperature + (initial_temperature - ambient_temperature) * fraction_remaining


def spacecraft_equilibrium_temperature(
    solar_flux: float,
    absorptivity: float,
    emissivity: float,
    area_absorbing: float,
    area_emitting: float,
) -> float:
    """Estimate a spacecraft's simple radiative-equilibrium temperature.

    Balances absorbed solar power against emitted thermal-IR power:
    ``alpha*S*A_abs = eps*sigma*A_emit*T^4``, so
    ``T = (alpha*S*A_abs / (eps*sigma*A_emit))^0.25``.

    Parameters
    ----------
    solar_flux:
        Incident solar flux, W/m^2 (e.g. ~1361 W/m^2 at Earth's mean
        distance from the Sun).
    absorptivity:
        Solar absorptivity of the sun-facing surface, dimensionless, in
        ``(0, 1]``.
    emissivity:
        Infrared emissivity of the radiating surface, dimensionless, in
        ``(0, 1]``.
    area_absorbing:
        Sun-facing projected area, m^2, > 0.
    area_emitting:
        Total radiating (emitting) surface area, m^2, > 0.

    Returns
    -------
    float
        Equilibrium temperature, K.

    Example
    -------
    A spherical satellite (area_emitting = 4x area_absorbing for a
    sphere) with typical white-paint-like properties:

    >>> round(
    ...     spacecraft_equilibrium_temperature(
    ...         solar_flux=1361.0, absorptivity=0.2, emissivity=0.85,
    ...         area_absorbing=1.0, area_emitting=4.0,
    ...     ),
    ...     1,
    ... )
    193.8

    """
    if solar_flux <= 0:
        raise InvalidThermalInputError(f"solar_flux must be positive, got {solar_flux!r}")
    if not (0 < absorptivity <= 1):
        raise InvalidThermalInputError(f"absorptivity must be in (0, 1], got {absorptivity!r}")
    if not (0 < emissivity <= 1):
        raise InvalidThermalInputError(f"emissivity must be in (0, 1], got {emissivity!r}")
    if area_absorbing <= 0:
        raise InvalidThermalInputError(f"area_absorbing must be positive, got {area_absorbing!r}")
    if area_emitting <= 0:
        raise InvalidThermalInputError(f"area_emitting must be positive, got {area_emitting!r}")

    absorbed_power = absorptivity * solar_flux * area_absorbing
    denominator = emissivity * STEFAN_BOLTZMANN_CONSTANT * area_emitting
    return float((absorbed_power / denominator) ** 0.25)
