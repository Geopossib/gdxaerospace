"""Conduction, convection, and radiation heat transfer; thermal resistance networks.

Reference
---------
- Incropera, F.P. & DeWitt, D.P., *Fundamentals of Heat and Mass
  Transfer*, 6th ed., Ch. 1-3 (Fourier's law, Newton's law of cooling,
  the Stefan-Boltzmann law, and the thermal-resistance-network analogy
  to electrical circuits).
- The Stefan-Boltzmann constant, 5.670374419e-8 W/(m^2*K^4), is an
  exactly defined SI constant since the 2019 redefinition (derived from
  the fixed values of the Boltzmann constant, Planck constant, and
  speed of light) -- not a measured value with uncertainty.

Assumptions
-----------
- Steady-state, one-dimensional heat transfer for the conduction/
  convection/resistance formulas (standard "lumped" treatment); no
  contact resistance between layers in the series/parallel network
  functions unless explicitly included as its own resistance term.
- Radiation exchange assumes both surfaces behave as ideal or
  gray-body radiators exchanging directly with each other (or with a
  surroundings temperature), not the more general view-factor-network
  treatment needed for complex multi-surface enclosures.
"""

from __future__ import annotations

from aerothermal.exceptions import InvalidThermalInputError

#: Stefan-Boltzmann constant, W/(m^2*K^4). Exact SI-defined value.
STEFAN_BOLTZMANN_CONSTANT = 5.670374419e-8


def conduction_heat_transfer(
    thermal_conductivity: float, area: float, delta_temperature: float, thickness: float
) -> float:
    """Compute the steady-state conductive heat transfer rate (Fourier's law).

    ``Q = k*A*dT/L``.

    Parameters
    ----------
    thermal_conductivity:
        Material thermal conductivity, W/(m*K), > 0.
    area:
        Cross-sectional area normal to the heat flow direction, m^2, > 0.
    delta_temperature:
        Temperature difference across the thickness, K.
    thickness:
        Conduction path length, m, > 0.

    Example
    -------
    >>> round(
    ...     conduction_heat_transfer(
    ...         thermal_conductivity=200.0, area=0.5, delta_temperature=50.0, thickness=0.01
    ...     ),
    ...     1,
    ... )
    500000.0

    """
    if thermal_conductivity <= 0:
        raise InvalidThermalInputError(
            f"thermal_conductivity must be positive, got {thermal_conductivity!r}"
        )
    if area <= 0:
        raise InvalidThermalInputError(f"area must be positive, got {area!r}")
    if thickness <= 0:
        raise InvalidThermalInputError(f"thickness must be positive, got {thickness!r}")
    return thermal_conductivity * area * delta_temperature / thickness


def convection_heat_transfer(
    convection_coefficient: float, area: float, delta_temperature: float
) -> float:
    """Compute the convective heat transfer rate (Newton's law of cooling): ``Q = h*A*dT``.

    Parameters
    ----------
    convection_coefficient:
        Convective heat transfer coefficient, W/(m^2*K), > 0.
    area:
        Surface area, m^2, > 0.
    delta_temperature:
        Temperature difference between the surface and the fluid, K.

    Example
    -------
    >>> round(
    ...     convection_heat_transfer(
    ...         convection_coefficient=25.0, area=2.0, delta_temperature=30.0
    ...     ),
    ...     1,
    ... )
    1500.0

    """
    if convection_coefficient <= 0:
        raise InvalidThermalInputError(
            f"convection_coefficient must be positive, got {convection_coefficient!r}"
        )
    if area <= 0:
        raise InvalidThermalInputError(f"area must be positive, got {area!r}")
    return convection_coefficient * area * delta_temperature


def radiation_heat_transfer(
    emissivity: float, area: float, hot_temperature: float, cold_temperature: float
) -> float:
    """Compute the net radiative heat transfer rate (Stefan-Boltzmann law).

    ``Q = eps*sigma*A*(T_h^4-T_c^4)``.

    Parameters
    ----------
    emissivity:
        Surface emissivity, dimensionless, in ``(0, 1]``.
    area:
        Radiating surface area, m^2, > 0.
    hot_temperature:
        Hot-side absolute temperature, K, > 0.
    cold_temperature:
        Cold-side (surroundings) absolute temperature, K, > 0.

    Example
    -------
    >>> round(
    ...     radiation_heat_transfer(
    ...         emissivity=0.9, area=1.0, hot_temperature=400.0, cold_temperature=300.0
    ...     ),
    ...     2,
    ... )
    893.08

    """
    if not (0 < emissivity <= 1):
        raise InvalidThermalInputError(f"emissivity must be in (0, 1], got {emissivity!r}")
    if area <= 0:
        raise InvalidThermalInputError(f"area must be positive, got {area!r}")
    if hot_temperature <= 0 or cold_temperature <= 0:
        raise InvalidThermalInputError("temperatures must be positive (absolute, Kelvin)")
    return (
        emissivity
        * STEFAN_BOLTZMANN_CONSTANT
        * area
        * (hot_temperature**4 - cold_temperature**4)
    )


def thermal_resistance_conduction(
    thickness: float, thermal_conductivity: float, area: float
) -> float:
    """Compute the conductive thermal resistance: ``R = L / (k*A)``.

    Parameters
    ----------
    thickness:
        Conduction path length, m, > 0.
    thermal_conductivity:
        Thermal conductivity, W/(m*K), > 0.
    area:
        Cross-sectional area, m^2, > 0.

    Returns
    -------
    float
        Thermal resistance, K/W.

    Example
    -------
    >>> round(
    ...     thermal_resistance_conduction(thickness=0.01, thermal_conductivity=200.0, area=0.5), 6
    ... )
    0.0001

    """
    if thickness <= 0:
        raise InvalidThermalInputError(f"thickness must be positive, got {thickness!r}")
    if thermal_conductivity <= 0:
        raise InvalidThermalInputError(
            f"thermal_conductivity must be positive, got {thermal_conductivity!r}"
        )
    if area <= 0:
        raise InvalidThermalInputError(f"area must be positive, got {area!r}")
    return thickness / (thermal_conductivity * area)


def thermal_resistance_convection(convection_coefficient: float, area: float) -> float:
    """Compute the convective thermal resistance: ``R = 1 / (h*A)``.

    Parameters
    ----------
    convection_coefficient:
        Convective heat transfer coefficient, W/(m^2*K), > 0.
    area:
        Surface area, m^2, > 0.

    Returns
    -------
    float
        Thermal resistance, K/W.

    Example
    -------
    >>> round(thermal_resistance_convection(convection_coefficient=25.0, area=2.0), 4)
    0.02

    """
    if convection_coefficient <= 0:
        raise InvalidThermalInputError(
            f"convection_coefficient must be positive, got {convection_coefficient!r}"
        )
    if area <= 0:
        raise InvalidThermalInputError(f"area must be positive, got {area!r}")
    return 1 / (convection_coefficient * area)


def series_resistance(*resistances: float) -> float:
    """Combine thermal resistances in series: ``R_total = sum(R_i)``.

    Parameters
    ----------
    *resistances:
        One or more thermal resistances, K/W, each > 0.

    Example
    -------
    >>> round(series_resistance(0.0001, 0.02), 4)
    0.0201

    """
    if len(resistances) == 0:
        raise InvalidThermalInputError("at least one resistance must be given")
    if any(r <= 0 for r in resistances):
        raise InvalidThermalInputError("all resistances must be positive")
    return sum(resistances)


def parallel_resistance(*resistances: float) -> float:
    """Combine thermal resistances in parallel: ``1/R_total = sum(1/R_i)``.

    Parameters
    ----------
    *resistances:
        One or more thermal resistances, K/W, each > 0.

    Example
    -------
    >>> round(parallel_resistance(0.02, 0.02), 4)
    0.01

    """
    if len(resistances) == 0:
        raise InvalidThermalInputError("at least one resistance must be given")
    if any(r <= 0 for r in resistances):
        raise InvalidThermalInputError("all resistances must be positive")
    return 1 / sum(1 / r for r in resistances)
