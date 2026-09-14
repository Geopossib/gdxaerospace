"""Convenience classes wrapping the ideal electrostatic-thruster relations.

Reference
---------
See :mod:`electricprop.ion_acceleration` for the underlying equations and
citations. These classes add no new physics -- they simply bundle a
thruster's operating parameters (voltage, current, mass flow, propellant)
into an object with method-style access, matching common usage patterns
in mission-analysis scripts.

Assumptions
-----------
- ``current`` is treated as the ion beam current for thrust purposes but
  as the *total* discharge current for power purposes (``P = V * I``).
  For a Hall thruster this is a reasonable first-order approximation
  since most discharge current is carried by the ion beam; for a gridded
  ion thruster, beam current and total current can differ more
  significantly and a more detailed power budget should be used for
  serious design work.
"""

from __future__ import annotations

from dataclasses import dataclass

from plasmathrust.constants import ION_MASS

from electricprop.ion_acceleration import (
    G0,
    ion_exhaust_velocity,
    specific_impulse_electric,
    thrust_efficiency,
)


@dataclass
class ElectrostaticThruster:
    """Base class for a simple electrostatically-accelerated ion thruster.

    Parameters
    ----------
    voltage:
        Net accelerating voltage, V, > 0.
    current:
        Discharge (approximately beam) current, A, > 0.
    mass_flow:
        Propellant mass flow rate, kg/s, > 0.
    propellant:
        Propellant name, must be a key in
        ``plasmathrust.constants.ION_MASS`` (default ``"xenon"``).
    charge_number:
        Ion charge state, >= 1 (default 1, singly ionized).

    """

    voltage: float
    current: float
    mass_flow: float
    propellant: str = "xenon"
    charge_number: int = 1

    def _ion_mass(self) -> float:
        try:
            return ION_MASS[self.propellant]
        except KeyError as exc:
            valid = ", ".join(sorted(ION_MASS))
            raise ValueError(
                f"Unknown propellant {self.propellant!r}; expected one of: {valid}. "
                "For a custom propellant, pass its ion mass directly to the "
                "electricprop.ion_acceleration functions instead."
            ) from exc

    def exhaust_velocity(self) -> float:
        """Ideal exhaust velocity, m/s. See :func:`ion_exhaust_velocity`."""
        return ion_exhaust_velocity(
            self.voltage, self._ion_mass(), charge_number=self.charge_number
        )

    def thrust(self) -> float:
        """Ideal thrust from mass flow and exhaust velocity, N: ``F = mdot * Ve``."""
        return self.mass_flow * self.exhaust_velocity()

    def power(self) -> float:
        """Total input electrical power, W: ``P = V * I``."""
        return self.voltage * self.current

    def specific_impulse(self, *, g0: float = G0) -> float:
        """Specific impulse, s. See :func:`specific_impulse_electric`."""
        return specific_impulse_electric(self.exhaust_velocity(), g0=g0)

    def efficiency(self) -> float:
        """Total thrust efficiency. See :func:`thrust_efficiency`."""
        return thrust_efficiency(self.thrust(), self.mass_flow, self.power())


@dataclass
class HallThruster(ElectrostaticThruster):
    """A Hall-effect thruster.

    Uses the same ideal electrostatic relations as :class:`ElectrostaticThruster`.

    Example
    -------
    >>> thruster = HallThruster(voltage=300.0, current=5.0, mass_flow=5e-6)
    >>> round(thruster.thrust(), 4)
    0.105
    >>> round(thruster.specific_impulse(), 1)
    2141.2
    >>> round(thruster.efficiency(), 3)
    0.735

    """


@dataclass
class IonThruster(ElectrostaticThruster):
    """A gridded ion thruster.

    Uses the same ideal electrostatic relations as :class:`ElectrostaticThruster`.

    Example
    -------
    >>> thruster = IonThruster(voltage=1200.0, current=1.76, mass_flow=3.4e-6, propellant="xenon")
    >>> round(thruster.specific_impulse(), 0)
    4282.0

    """
