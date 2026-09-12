"""Ideal-cycle compressor and turbine stage temperature/work relations.

Reference
---------
- Mattingly, J.D., *Elements of Gas Turbine Propulsion*, 2nd ed., Ch. 5
  (compressor and turbine component analysis, isentropic-efficiency
  definitions).
- Cohen, H., Rogers, G.F.C. & Saravanamuttoo, H.I.H., *Gas Turbine
  Theory*, 4th ed., Ch. 2, for the same relations in the Brayton-cycle
  context.

Assumptions
-----------
- Calorically perfect gas (constant gamma, cp) across each component —
  a simplification; real gas-turbine analysis uses temperature-dependent
  gas properties, especially across the turbine.
- Adiabatic stage (no heat loss to the casing).
- Isentropic efficiency is defined per the standard convention:
  compressor ``eta_c = dT_ideal / dT_actual`` (actual work always exceeds
  ideal for a compressor); turbine ``eta_t = dT_actual / dT_ideal``
  (actual work is always less than ideal for a turbine).
"""

from __future__ import annotations

from turbomachpy.exceptions import InvalidTurbomachineryInputError


def _check_common(
    inlet_temperature: float, pressure_ratio: float, isentropic_efficiency: float
) -> None:
    if inlet_temperature <= 0:
        raise InvalidTurbomachineryInputError(
            f"inlet_temperature must be positive, got {inlet_temperature!r}"
        )
    if pressure_ratio <= 1:
        raise InvalidTurbomachineryInputError(
            f"pressure_ratio must be > 1, got {pressure_ratio!r}"
        )
    if not (0 < isentropic_efficiency <= 1):
        raise InvalidTurbomachineryInputError(
            f"isentropic_efficiency must be in (0, 1], got {isentropic_efficiency!r}"
        )


def compressor_temperature_rise(
    inlet_temperature: float,
    pressure_ratio: float,
    isentropic_efficiency: float,
    *,
    gamma: float = 1.4,
) -> float:
    """Actual compressor stagnation-temperature rise for a given pressure ratio.

    ``dT_ideal = T1 * (PR^((gamma-1)/gamma) - 1)``,
    ``dT_actual = dT_ideal / eta_c``.

    Parameters
    ----------
    inlet_temperature:
        Compressor inlet stagnation temperature, K, > 0.
    pressure_ratio:
        Stagnation pressure ratio across the compressor, > 1.
    isentropic_efficiency:
        Compressor isentropic efficiency, in ``(0, 1]``.
    gamma:
        Ratio of specific heats of the working gas.

    Returns
    -------
    float
        Actual stagnation-temperature rise, K.

    Example
    -------
    >>> round(
    ...     compressor_temperature_rise(
    ...         inlet_temperature=288.0, pressure_ratio=8.0, isentropic_efficiency=0.85
    ...     ),
    ...     1,
    ... )
    274.9

    """
    _check_common(inlet_temperature, pressure_ratio, isentropic_efficiency)
    ideal_rise = inlet_temperature * (
        pressure_ratio ** ((gamma - 1) / gamma) - 1
    )
    return float(ideal_rise / isentropic_efficiency)


def turbine_temperature_drop(
    inlet_temperature: float,
    pressure_ratio: float,
    isentropic_efficiency: float,
    *,
    gamma: float = 1.333,
) -> float:
    """Actual turbine stagnation-temperature drop for a given pressure ratio.

    ``dT_ideal = T3 * (1 - (1/PR)^((gamma-1)/gamma))``,
    ``dT_actual = eta_t * dT_ideal``.

    Parameters
    ----------
    inlet_temperature:
        Turbine inlet stagnation temperature, K, > 0.
    pressure_ratio:
        Stagnation pressure ratio across the turbine, > 1.
    isentropic_efficiency:
        Turbine isentropic efficiency, in ``(0, 1]``.
    gamma:
        Ratio of specific heats of the working gas. Defaults to 1.333,
        a typical value for hot combustion-product gas (lower than the
        1.4 used for cold air in the compressor, reflecting the higher
        specific heat of combustion products).

    Returns
    -------
    float
        Actual stagnation-temperature drop, K.

    Example
    -------
    >>> round(
    ...     turbine_temperature_drop(
    ...         inlet_temperature=1100.0, pressure_ratio=8.0, isentropic_efficiency=0.90
    ...     ),
    ...     1,
    ... )
    401.1

    """
    _check_common(inlet_temperature, pressure_ratio, isentropic_efficiency)
    ideal_drop = inlet_temperature * (1 - (1 / pressure_ratio) ** ((gamma - 1) / gamma))
    return float(isentropic_efficiency * ideal_drop)


def specific_work(specific_heat: float, temperature_change: float) -> float:
    """Specific shaft work: ``w = cp * dT``.

    Parameters
    ----------
    specific_heat:
        Constant-pressure specific heat of the working gas, J/(kg*K), > 0.
    temperature_change:
        Stagnation-temperature rise (compressor) or drop (turbine), K.
        Sign is preserved: pass a positive value from
        :func:`compressor_temperature_rise` or
        :func:`turbine_temperature_drop` for the magnitude of specific
        work in each case.

    Returns
    -------
    float
        Specific work, J/kg.

    Example
    -------
    >>> round(specific_work(specific_heat=1005.0, temperature_change=274.9), 0)
    276274.0

    """
    if specific_heat <= 0:
        raise InvalidTurbomachineryInputError(
            f"specific_heat must be positive, got {specific_heat!r}"
        )
    return specific_heat * temperature_change
