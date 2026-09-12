"""Core flow-property calculations: dynamic pressure, Mach number, Reynolds number.

Reference
---------
- Anderson, J.D., *Fundamentals of Aerodynamics*, 6th ed., Ch. 1-4.
- White, F.M., *Viscous Fluid Flow*, for Reynolds number and viscosity model.

Assumptions
-----------
- Continuum, calorically perfect gas (constant specific heats) unless noted.
- Sutherland's law is used for dynamic viscosity of air.
"""

from __future__ import annotations

from aerocalc.exceptions import InvalidMachNumberError

#: Sutherland's law reference viscosity, Pa*s, for air.
_SUTHERLAND_MU_REF = 1.716e-5
#: Sutherland's law reference temperature, K.
_SUTHERLAND_T_REF = 273.15
#: Sutherland's constant for air, K.
_SUTHERLAND_S = 110.4


def dynamic_pressure(density: float, velocity: float) -> float:
    """Freestream dynamic pressure ``q = 1/2 * rho * V^2``.

    Parameters
    ----------
    density:
        Fluid density, kg/m^3. Must be positive.
    velocity:
        Freestream velocity magnitude, m/s.

    Returns
    -------
    float
        Dynamic pressure in Pascal.

    Raises
    ------
    ValueError
        If ``density`` is not positive.

    Example
    -------
    >>> round(dynamic_pressure(density=1.225, velocity=100), 2)
    6125.0

    """
    if density <= 0:
        raise ValueError(
            f"density must be positive, got {density!r}. "
            "Use aerocalc.Atmosphere(altitude=...).density for a physically "
            "valid value."
        )
    return 0.5 * density * velocity**2


def mach_number(velocity: float, speed_of_sound: float) -> float:
    """Mach number ``M = V / a``.

    Parameters
    ----------
    velocity:
        Flow velocity, m/s. May be negative (direction), magnitude is used.
    speed_of_sound:
        Local speed of sound, m/s. Must be positive.

    Returns
    -------
    float
        Mach number (dimensionless).

    Raises
    ------
    InvalidMachNumberError
        If ``speed_of_sound`` is not positive.

    Example
    -------
    >>> round(mach_number(velocity=343.0, speed_of_sound=343.0), 3)
    1.0

    """
    if speed_of_sound <= 0:
        raise InvalidMachNumberError(
            mach=float("nan"),
            reason=f"speed_of_sound must be positive, got {speed_of_sound!r}",
        )
    return abs(velocity) / speed_of_sound


def sutherland_viscosity(temperature: float) -> float:
    """Dynamic viscosity of air via Sutherland's law.

    Parameters
    ----------
    temperature:
        Static temperature, Kelvin. Must be positive.

    Returns
    -------
    float
        Dynamic viscosity, Pa*s (kg/(m*s)).

    Raises
    ------
    ValueError
        If ``temperature`` is not positive.

    Notes
    -----
    Valid to within ~2% for air from roughly 170 K to 1900 K
    (White, *Viscous Fluid Flow*).

    Example
    -------
    >>> round(sutherland_viscosity(288.15) * 1e5, 3)
    1.789

    """
    if temperature <= 0:
        raise ValueError(f"temperature must be positive Kelvin, got {temperature!r}")
    t_ratio = temperature / _SUTHERLAND_T_REF
    return float(
        _SUTHERLAND_MU_REF
        * t_ratio**1.5
        * (_SUTHERLAND_T_REF + _SUTHERLAND_S)
        / (temperature + _SUTHERLAND_S)
    )


def reynolds_number(
    density: float,
    velocity: float,
    length: float,
    *,
    temperature: float | None = None,
    dynamic_viscosity: float | None = None,
) -> float:
    """Reynolds number ``Re = rho * V * L / mu``.

    Parameters
    ----------
    density:
        Fluid density, kg/m^3. Must be positive.
    velocity:
        Freestream velocity magnitude, m/s.
    length:
        Characteristic length, m (e.g. chord length). Must be positive.
    temperature:
        Static temperature, K. If given (and ``dynamic_viscosity`` is not),
        viscosity is computed from Sutherland's law.
    dynamic_viscosity:
        Dynamic viscosity, Pa*s. Takes precedence over ``temperature`` if
        both are given.

    Returns
    -------
    float
        Reynolds number (dimensionless).

    Raises
    ------
    ValueError
        If neither ``temperature`` nor ``dynamic_viscosity`` is given, or if
        ``density``/``length`` are not positive.

    Example
    -------
    >>> re = reynolds_number(density=1.225, velocity=50, length=1.0, temperature=288.15)
    >>> round(re, -3)
    3423000.0

    """
    if density <= 0:
        raise ValueError(f"density must be positive, got {density!r}")
    if length <= 0:
        raise ValueError(f"length must be positive, got {length!r}")
    if dynamic_viscosity is None:
        if temperature is None:
            raise ValueError(
                "reynolds_number requires either 'dynamic_viscosity' or "
                "'temperature' (to derive viscosity via Sutherland's law)."
            )
        dynamic_viscosity = sutherland_viscosity(temperature)
    if dynamic_viscosity <= 0:
        raise ValueError(f"dynamic_viscosity must be positive, got {dynamic_viscosity!r}")

    return density * abs(velocity) * length / dynamic_viscosity
