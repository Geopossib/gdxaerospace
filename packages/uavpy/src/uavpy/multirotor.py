"""Multirotor hover power (actuator-disk momentum theory) and flight-time estimation.

Reference
---------
- Leishman, J.G., *Principles of Helicopter Aerodynamics*, 2nd ed.,
  Ch. 2 (actuator disk / momentum theory for ideal induced hover power).
- The "figure of merit" (FM), the ratio of ideal induced power to actual
  power, is a standard rotor efficiency metric (Leishman Ch. 2); small
  multirotor propellers typically achieve FM ~ 0.5-0.7, well below a
  large, well-designed helicopter rotor's ~0.75-0.8, due to Reynolds-
  number and blade-design effects at small scale.

Assumptions
-----------
- Ideal (induced-power-only) hover: momentum theory gives the minimum
  possible power to hover, ignoring profile drag, tip losses, and
  interference between rotors -- all folded into the empirical figure
  of merit here rather than modeled individually.
- Battery usable-capacity fraction (default 0.8) accounts for the fact
  that fully discharging a battery is avoided in practice; this is a
  simplification, not a discharge-curve model.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from uavpy.exceptions import InvalidUAVInputError

#: Standard gravitational acceleration, m/s^2.
G0 = 9.80665


def ideal_hover_power(thrust: float, total_disk_area: float, air_density: float = 1.225) -> float:
    """Compute the ideal (momentum-theory) induced power to hover.

    ``P_ideal = T^1.5 / sqrt(2*rho*A)``.

    Parameters
    ----------
    thrust:
        Total thrust required (equals weight, for hover), N, > 0.
    total_disk_area:
        Combined rotor disk area of all rotors, m^2, > 0.
    air_density:
        Air density, kg/m^3, > 0. Defaults to sea-level ISA.

    Returns
    -------
    float
        Ideal induced hover power, W.

    Example
    -------
    >>> round(ideal_hover_power(thrust=24.52, total_disk_area=0.2027), 2)
    172.29

    """
    if thrust <= 0:
        raise InvalidUAVInputError(f"thrust must be positive, got {thrust!r}")
    if total_disk_area <= 0:
        raise InvalidUAVInputError(f"total_disk_area must be positive, got {total_disk_area!r}")
    if air_density <= 0:
        raise InvalidUAVInputError(f"air_density must be positive, got {air_density!r}")
    return thrust**1.5 / math.sqrt(2 * air_density * total_disk_area)


def actual_hover_power(
    thrust: float,
    total_disk_area: float,
    *,
    figure_of_merit: float = 0.6,
    air_density: float = 1.225,
) -> float:
    """Compute the actual hover power, accounting for rotor efficiency losses.

    ``P_actual = P_ideal / FM``.

    Parameters
    ----------
    thrust:
        Total thrust required, N, > 0.
    total_disk_area:
        Combined rotor disk area, m^2, > 0.
    figure_of_merit:
        Rotor figure of merit, in ``(0, 1]``. Defaults to 0.6, typical
        for small multirotor propellers.
    air_density:
        Air density, kg/m^3, > 0.

    Returns
    -------
    float
        Actual hover power, W.

    Example
    -------
    >>> round(actual_hover_power(thrust=24.52, total_disk_area=0.2027), 2)
    287.16

    """
    if not (0 < figure_of_merit <= 1):
        raise InvalidUAVInputError(
            f"figure_of_merit must be in (0, 1], got {figure_of_merit!r}"
        )
    return ideal_hover_power(thrust, total_disk_area, air_density) / figure_of_merit


@dataclass
class Multirotor:
    """A simple multirotor UAV performance model.

    Parameters
    ----------
    mass:
        Total UAV mass (including battery and payload), kg, > 0.
    num_motors:
        Number of motors/rotors, > 0.
    rotor_radius:
        Rotor radius, m, > 0 (all rotors assumed identical).
    battery_voltage:
        Nominal battery voltage, V, > 0.
    battery_capacity_mah:
        Battery capacity, mAh, > 0.
    figure_of_merit:
        Rotor figure of merit, in ``(0, 1]``. Defaults to 0.6.
    usable_capacity_fraction:
        Fraction of nominal battery capacity usable in practice
        (avoiding full discharge), in ``(0, 1]``. Defaults to 0.8.

    """

    mass: float
    num_motors: int
    rotor_radius: float
    battery_voltage: float
    battery_capacity_mah: float
    figure_of_merit: float = 0.6
    usable_capacity_fraction: float = 0.8

    def __post_init__(self) -> None:
        if self.mass <= 0:
            raise InvalidUAVInputError(f"mass must be positive, got {self.mass!r}")
        if self.num_motors <= 0:
            raise InvalidUAVInputError(f"num_motors must be positive, got {self.num_motors!r}")
        if self.rotor_radius <= 0:
            raise InvalidUAVInputError(
                f"rotor_radius must be positive, got {self.rotor_radius!r}"
            )
        if self.battery_voltage <= 0:
            raise InvalidUAVInputError(
                f"battery_voltage must be positive, got {self.battery_voltage!r}"
            )
        if self.battery_capacity_mah <= 0:
            raise InvalidUAVInputError(
                f"battery_capacity_mah must be positive, got {self.battery_capacity_mah!r}"
            )
        if not (0 < self.usable_capacity_fraction <= 1):
            raise InvalidUAVInputError(
                "usable_capacity_fraction must be in (0, 1], got "
                f"{self.usable_capacity_fraction!r}"
            )

    def weight(self, *, g0: float = G0) -> float:
        """Total weight, N."""
        return self.mass * g0

    def total_disk_area(self) -> float:
        """Compute the combined rotor disk area of all rotors, m^2."""
        return self.num_motors * math.pi * self.rotor_radius**2

    def thrust_to_weight(self, max_thrust_per_motor: float) -> float:
        """Compute thrust-to-weight ratio at a given per-motor maximum thrust.

        Parameters
        ----------
        max_thrust_per_motor:
            Maximum thrust available from a single motor, N, > 0.

        """
        if max_thrust_per_motor <= 0:
            raise InvalidUAVInputError(
                f"max_thrust_per_motor must be positive, got {max_thrust_per_motor!r}"
            )
        total_max_thrust = self.num_motors * max_thrust_per_motor
        return total_max_thrust / self.weight()

    def hover_power(self, *, air_density: float = 1.225) -> float:
        """Estimate the total hover power draw, W."""
        return actual_hover_power(
            self.weight(),
            self.total_disk_area(),
            figure_of_merit=self.figure_of_merit,
            air_density=air_density,
        )

    def battery_energy_wh(self) -> float:
        """Total (nominal) battery energy, Wh."""
        return self.battery_voltage * self.battery_capacity_mah / 1000

    def flight_time_minutes(self, *, air_density: float = 1.225) -> float:
        """Estimate hover flight time, minutes, using the usable battery capacity."""
        usable_energy_wh = self.battery_energy_wh() * self.usable_capacity_fraction
        hours = usable_energy_wh / self.hover_power(air_density=air_density)
        return hours * 60
