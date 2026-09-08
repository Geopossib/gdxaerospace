"""Combustion stoichiometry and a simplified adiabatic temperature-rise estimate.

Reference
---------
- Turns, S.R., *An Introduction to Combustion*, 3rd ed., Ch. 2
  (stoichiometry of hydrocarbon-air combustion, Eq. 2.1-2.6). Reference
  stoichiometric air-fuel ratios (methane ~17.2, octane ~15.1 by mass)
  checked against Turns Table 2.1 / standard combustion references.
- Cohen, H., Rogers, G.F.C. & Saravanamuttoo, H.I.H., *Gas Turbine
  Theory*, 4th ed., Ch. 6, for the general energy-balance framing of
  combustor temperature rise (though this module uses a single constant
  cp rather than their variable-cp gas-property charts — see the
  ``temperature_rise_estimate`` docstring for the resulting limitation).

Assumptions
-----------
- Fuel is a pure hydrocarbon (or hydrocarbon-oxygenate) ``CxHyOz``;
  complete combustion to CO2 and H2O only (no dissociation, no CO/soot).
- Air is modeled as 21% O2 / 79% N2 by mole, mean molar mass 28.97 g/mol
  (dry air, no humidity).
- ``temperature_rise_estimate`` uses a single constant specific heat for
  the products, which is a first-order simplification: real combustion
  gas cp rises significantly with temperature, so this will overestimate
  the temperature rise at high fuel/air ratios relative to a real
  (variable-cp or equilibrium) calculation. It is adequate for
  conceptual-design estimates only.
"""

from __future__ import annotations

from combustionpy.exceptions import InvalidFuelCompositionError

#: Molar mass of dry air, g/mol.
_MOLAR_MASS_AIR = 28.97
#: Mole fraction of O2 in dry air.
_O2_MOLE_FRACTION_AIR = 0.21
#: Atomic weights, g/mol.
_ATOMIC_WEIGHT_C = 12.011
_ATOMIC_WEIGHT_H = 1.008
_ATOMIC_WEIGHT_O = 16.00


def stoichiometric_air_fuel_ratio(carbon: float, hydrogen: float, oxygen: float = 0.0) -> float:
    """Stoichiometric (mass-basis) air-fuel ratio for a ``CxHyOz`` hydrocarbon fuel.

    Balances ``CxHyOz + a(O2 + 3.76 N2) -> x CO2 + (y/2) H2O + 3.76a N2``
    for the required moles of O2 per mole of fuel,
    ``a = x + y/4 - z/2``, then converts to a mass-basis air-fuel ratio.

    Parameters
    ----------
    carbon:
        Number of carbon atoms per fuel molecule (``x``), >= 0.
    hydrogen:
        Number of hydrogen atoms per fuel molecule (``y``), > 0.
    oxygen:
        Number of oxygen atoms already in the fuel molecule (``z``), >= 0
        (e.g. 1 for methanol CH3OH -> C1H4O1).

    Returns
    -------
    float
        Stoichiometric air-fuel ratio, kg air / kg fuel.

    Raises
    ------
    InvalidFuelCompositionError
        If the composition is invalid (negative atom counts, zero
        hydrogen and carbon, or a composition requiring negative O2).

    Example
    -------
    >>> round(stoichiometric_air_fuel_ratio(carbon=1, hydrogen=4), 2)  # methane, CH4
    17.2
    >>> round(stoichiometric_air_fuel_ratio(carbon=8, hydrogen=18), 2)  # octane, C8H18
    15.1

    """
    if carbon < 0 or hydrogen < 0 or oxygen < 0:
        raise InvalidFuelCompositionError("atom counts (carbon, hydrogen, oxygen) must be >= 0")
    if carbon == 0 and hydrogen == 0:
        raise InvalidFuelCompositionError("fuel must contain at least one carbon or hydrogen atom")

    moles_o2_required = carbon + hydrogen / 4 - oxygen / 2
    if moles_o2_required <= 0:
        raise InvalidFuelCompositionError(
            f"composition C{carbon}H{hydrogen}O{oxygen} requires no external oxygen "
            "(already fully oxidized) -- not combustible in the usual sense"
        )

    molar_mass_fuel = (
        carbon * _ATOMIC_WEIGHT_C + hydrogen * _ATOMIC_WEIGHT_H + oxygen * _ATOMIC_WEIGHT_O
    )
    moles_air_required = moles_o2_required / _O2_MOLE_FRACTION_AIR
    mass_air_required = moles_air_required * _MOLAR_MASS_AIR

    return mass_air_required / molar_mass_fuel


def equivalence_ratio(actual_air_fuel_ratio: float, stoichiometric_air_fuel_ratio_: float) -> float:
    """Equivalence ratio ``phi = (A/F)_stoich / (A/F)_actual``.

    ``phi = 1``: stoichiometric. ``phi > 1``: fuel-rich. ``phi < 1``: fuel-lean.

    Parameters
    ----------
    actual_air_fuel_ratio:
        Actual air-fuel mass ratio, > 0.
    stoichiometric_air_fuel_ratio_:
        Stoichiometric air-fuel mass ratio for the same fuel, > 0. See
        :func:`stoichiometric_air_fuel_ratio`.

    Example
    -------
    >>> round(
    ...     equivalence_ratio(actual_air_fuel_ratio=20.0, stoichiometric_air_fuel_ratio_=17.19), 3
    ... )
    0.86

    """
    if actual_air_fuel_ratio <= 0:
        raise InvalidFuelCompositionError(
            f"actual_air_fuel_ratio must be positive, got {actual_air_fuel_ratio!r}"
        )
    if stoichiometric_air_fuel_ratio_ <= 0:
        raise InvalidFuelCompositionError(
            "stoichiometric_air_fuel_ratio_ must be positive, got "
            f"{stoichiometric_air_fuel_ratio_!r}"
        )
    return stoichiometric_air_fuel_ratio_ / actual_air_fuel_ratio


def temperature_rise_estimate(
    mdot_fuel: float,
    mdot_air: float,
    heating_value: float,
    *,
    specific_heat: float = 1150.0,
    combustion_efficiency: float = 1.0,
) -> float:
    """Simplified constant-cp adiabatic temperature rise from fuel combustion.

    ``dT = eta_c * mdot_fuel * LHV / ((mdot_air + mdot_fuel) * cp)``

    This is a first-order energy balance, **not** a full equilibrium
    flame-temperature calculation: it assumes a single constant specific
    heat for the combustion products, which becomes increasingly
    inaccurate (overestimating dT) as the fuel/air ratio rises, since real
    gas cp increases substantially with temperature. Use this for
    conceptual-design screening only.

    Parameters
    ----------
    mdot_fuel:
        Fuel mass flow rate, kg/s, > 0.
    mdot_air:
        Air mass flow rate, kg/s, > 0.
    heating_value:
        Lower heating value of the fuel, J/kg, > 0.
    specific_heat:
        Constant-pressure specific heat of the combustion products,
        J/(kg*K). Defaults to 1150 J/(kg*K), a typical mean value for hot
        combustion gas (Cohen, Rogers & Saravanamuttoo).
    combustion_efficiency:
        Fraction of the fuel's heating value actually released, in
        ``(0, 1]``. Defaults to 1.0 (ideal, complete combustion).

    Returns
    -------
    float
        Temperature rise, Kelvin, above the inlet (reactant) temperature.

    Example
    -------
    >>> round(
    ...     temperature_rise_estimate(mdot_fuel=0.5, mdot_air=25.0, heating_value=43e6),
    ...     1,
    ... )
    733.2

    """
    if mdot_fuel <= 0:
        raise InvalidFuelCompositionError(f"mdot_fuel must be positive, got {mdot_fuel!r}")
    if mdot_air <= 0:
        raise InvalidFuelCompositionError(f"mdot_air must be positive, got {mdot_air!r}")
    if heating_value <= 0:
        raise InvalidFuelCompositionError(f"heating_value must be positive, got {heating_value!r}")
    if not (0 < combustion_efficiency <= 1):
        raise InvalidFuelCompositionError(
            f"combustion_efficiency must be in (0, 1], got {combustion_efficiency!r}"
        )

    heat_released = combustion_efficiency * mdot_fuel * heating_value
    total_mass_flow = mdot_air + mdot_fuel
    return heat_released / (total_mass_flow * specific_heat)
