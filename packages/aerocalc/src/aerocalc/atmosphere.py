"""International Standard Atmosphere (ISA) model.

Implements the 1976 U.S. Standard Atmosphere / ICAO Doc 7488 seven-layer
model from sea level to 86 km geopotential altitude.

Reference
---------
- U.S. Standard Atmosphere, 1976, NOAA-S/T 76-1562.
- ICAO Doc 7488/3, *Manual of the ICAO Standard Atmosphere*.
- Anderson, J.D., *Introduction to Flight*, 8th ed., Ch. 3.

Assumptions
-----------
- Dry air, hydrostatic equilibrium, ideal-gas behavior.
- Geopotential altitude is used as the independent variable (the small
  difference from geometric altitude is neglected below 86 km, consistent
  with the standard's own definition).
- Valid strictly for 0 m <= altitude <= 86000 m. Outside this range, the
  standard atmosphere is undefined and :class:`~aerocalc.exceptions.InvalidAltitudeError`
  is raised.
"""

from __future__ import annotations

from dataclasses import dataclass

from aerocalc.exceptions import InvalidAltitudeError

#: Standard sea-level gravitational acceleration, m/s^2 (ICAO Doc 7488).
G0 = 9.80665

#: Specific gas constant for dry air, J/(kg*K).
R_AIR = 287.05287

#: Ratio of specific heats for air (calorically perfect gas assumption).
GAMMA_AIR = 1.4

#: Minimum and maximum altitude (m) supported by the standard-atmosphere model.
_ALT_MIN = 0.0
_ALT_MAX = 86_000.0

# Each layer: (base altitude [m], lapse rate [K/m], base temperature [K], base pressure [Pa])
# Base pressures are computed from the barometric formula chained layer-to-layer
# and match the published U.S. Standard Atmosphere 1976 table to 5 significant figures.
_LAYERS: tuple[tuple[float, float, float, float], ...] = (
    (0.0, -0.0065, 288.15, 101_325.0),
    (11_000.0, 0.0, 216.65, 22_632.06),
    (20_000.0, 0.001, 216.65, 5_474.889),
    (32_000.0, 0.0028, 228.65, 868.019),
    (47_000.0, 0.0, 270.65, 110.906),
    (51_000.0, -0.0028, 270.65, 66.939),
    (71_000.0, -0.002, 214.65, 3.956),
)


def _layer_for_altitude(altitude: float) -> tuple[float, float, float, float]:
    """Return the (base_alt, lapse_rate, base_temp, base_pressure) layer tuple."""
    layer = _LAYERS[0]
    for candidate in _LAYERS:
        if altitude >= candidate[0]:
            layer = candidate
        else:
            break
    return layer


@dataclass(frozen=True)
class AtmosphereState:
    """Immutable snapshot of standard-atmosphere properties at one altitude.

    All fields are SI units: Kelvin, Pascal, kg/m^3, m/s, meters.
    """

    altitude: float
    temperature: float
    pressure: float
    density: float
    speed_of_sound: float


class Atmosphere:
    """International Standard Atmosphere at a given geopotential altitude.

    Parameters
    ----------
    altitude:
        Geopotential altitude in meters, 0 <= altitude <= 86000.

    Raises
    ------
    InvalidAltitudeError
        If ``altitude`` is outside ``[0, 86000]`` meters.

    Example
    -------
    >>> atm = Atmosphere(altitude=11_000)
    >>> round(atm.temperature, 2)
    216.65
    >>> round(atm.pressure, 1)
    22632.1

    """

    def __init__(self, altitude: float) -> None:
        if not (_ALT_MIN <= altitude <= _ALT_MAX):
            raise InvalidAltitudeError(
                altitude, (_ALT_MIN, _ALT_MAX), model="ISA (1976 US Standard Atmosphere)"
            )
        self.altitude = float(altitude)
        self._state = self._compute_state(self.altitude)

    @staticmethod
    def _compute_state(altitude: float) -> AtmosphereState:
        base_alt, lapse_rate, base_temp, base_pressure = _layer_for_altitude(altitude)
        delta_h = altitude - base_alt
        temperature = base_temp + lapse_rate * delta_h

        if abs(lapse_rate) < 1e-12:
            pressure = base_pressure * pow(
                2.718281828459045, -G0 * delta_h / (R_AIR * base_temp)
            )
        else:
            pressure = base_pressure * (temperature / base_temp) ** (
                -G0 / (lapse_rate * R_AIR)
            )

        density = pressure / (R_AIR * temperature)
        speed_of_sound = (GAMMA_AIR * R_AIR * temperature) ** 0.5

        return AtmosphereState(
            altitude=altitude,
            temperature=temperature,
            pressure=pressure,
            density=density,
            speed_of_sound=speed_of_sound,
        )

    @property
    def temperature(self) -> float:
        """Static temperature, Kelvin."""
        return self._state.temperature

    @property
    def pressure(self) -> float:
        """Static pressure, Pascal."""
        return self._state.pressure

    @property
    def density(self) -> float:
        """Air density, kg/m^3."""
        return self._state.density

    @property
    def speed_of_sound(self) -> float:
        """Speed of sound, m/s, assuming a calorically perfect gas."""
        return self._state.speed_of_sound

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return (
            f"Atmosphere(altitude={self.altitude:.1f} m, "
            f"T={self.temperature:.2f} K, P={self.pressure:.1f} Pa, "
            f"rho={self.density:.5f} kg/m^3)"
        )
