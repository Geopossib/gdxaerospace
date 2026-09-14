"""Preliminary spacecraft-plasma interaction: floating potential of an isolated conductor.

Reference
---------
- Lieberman, M.A. & Lichtenberg, A.J., *Principles of Plasma Discharges
  and Materials Processing*, 2nd ed., Ch. 2 (electron thermal flux, Bohm
  ion flux, and the floating-potential current-balance derivation this
  module implements).
- Chen, F.F., *Introduction to Plasma Physics and Controlled Fusion*,
  3rd ed., Ch. 1, for the same result in a slightly different notation.
- Hastings, D. & Garrett, H., *Spacecraft-Environment Interactions*,
  Cambridge, 1996, for the spacecraft-charging application of this model.

Derivation
----------
An isolated conductor immersed in a plasma charges until the net current
to it is zero. Electrons, being far lighter than ions, would otherwise
arrive much faster, so the surface charges negative until the resulting
retarding field reduces the electron flux to match the (much slower) ion
flux. Balancing the random (one-sided, kinetic-theory) electron thermal
flux, reduced by the Boltzmann retarding factor, against the Bohm ion
flux entering the sheath gives:

``V_f = -(kTe / 2e) * ln(M / (2*pi*m_e))``

This module's numerical coefficients reproduce well-known reference
values, e.g. ``V_f ~= -4.68 * Te[eV]`` for singly-ionized argon and
``V_f ~= -5.27 * Te[eV]`` for singly-ionized xenon.

Assumptions
-----------
- Maxwellian electrons, ``Ti << Te`` (so ions arrive at the Bohm
  velocity), no secondary-electron emission, no photoemission, and no
  magnetic-field effects on the collected currents. Real spacecraft
  surfaces in sunlight can charge quite differently due to photoemission
  (often driving the potential positive rather than negative) -- this
  module captures only the plasma-electron/ion current-balance piece of
  a full spacecraft-charging analysis, and explicitly does NOT model
  photoemission, secondary emission, or differential charging between
  surfaces. Do not use this alone for a flight charging assessment.
"""

from __future__ import annotations

import math

from plasmathrust.constants import ELECTRON_MASS, ELEMENTARY_CHARGE
from plasmathrust.plasma_parameters import bohm_velocity

from plasmaspace.exceptions import InvalidSpacePlasmaInputError


def electron_thermal_flux(electron_density: float, electron_temperature_ev: float) -> float:
    """One-sided random electron thermal flux to a surface: ``Gamma_e0 = n_e * v_e_bar / 4``.

    ``v_e_bar = sqrt(8*kTe / (pi*m_e))`` is the mean speed of a Maxwellian
    electron distribution (Lieberman & Lichtenberg Eq. 2.4.6).

    Parameters
    ----------
    electron_density:
        Electron number density, m^-3, > 0.
    electron_temperature_ev:
        Electron temperature, eV, > 0.

    Returns
    -------
    float
        Electron flux, m^-2 s^-1.

    Example
    -------
    >>> round(electron_thermal_flux(electron_density=1e12, electron_temperature_ev=3.0), -15)
    2.9e+17

    """
    if electron_density <= 0:
        raise InvalidSpacePlasmaInputError(
            f"electron_density must be positive, got {electron_density!r}"
        )
    if electron_temperature_ev <= 0:
        raise InvalidSpacePlasmaInputError(
            f"electron_temperature_ev must be positive, got {electron_temperature_ev!r}"
        )
    kte = electron_temperature_ev * ELEMENTARY_CHARGE
    mean_speed = math.sqrt(8 * kte / (math.pi * ELECTRON_MASS))
    return electron_density * mean_speed / 4


def ion_bohm_flux(
    electron_density: float, electron_temperature_ev: float, ion_mass: float
) -> float:
    """Ion flux entering the sheath at the Bohm velocity: ``Gamma_i = n_e * u_B``.

    Parameters
    ----------
    electron_density:
        Electron (~= ion, quasi-neutral) number density, m^-3, > 0.
    electron_temperature_ev:
        Electron temperature, eV, > 0.
    ion_mass:
        Ion mass, kg, > 0.

    Returns
    -------
    float
        Ion flux, m^-2 s^-1.

    Example
    -------
    >>> from plasmathrust.constants import ION_MASS
    >>> round(
    ...     ion_bohm_flux(
    ...         electron_density=1e12, electron_temperature_ev=3.0, ion_mass=ION_MASS["argon"]
    ...     ),
    ...     -14,
    ... )
    2700000000000000.0

    """
    if electron_density <= 0:
        raise InvalidSpacePlasmaInputError(
            f"electron_density must be positive, got {electron_density!r}"
        )
    return electron_density * bohm_velocity(electron_temperature_ev, ion_mass)


def floating_potential(electron_temperature_ev: float, ion_mass: float) -> float:
    """Floating potential of an isolated conductor relative to the plasma potential.

    ``V_f = -(kTe / 2e) * ln(M / (2*pi*m_e))``, from balancing the
    retarded electron thermal flux against the Bohm ion flux (see the
    module docstring for the full derivation).

    Parameters
    ----------
    electron_temperature_ev:
        Electron temperature, eV, > 0.
    ion_mass:
        Ion mass, kg, > 0.

    Returns
    -------
    float
        Floating potential, V (negative, relative to the local plasma
        potential -- this is NOT an absolute spacecraft potential, which
        also depends on photoemission and other effects; see module
        docstring).

    Example
    -------
    >>> from plasmathrust.constants import ION_MASS
    >>> round(floating_potential(electron_temperature_ev=3.0, ion_mass=ION_MASS["argon"]), 2)
    -14.04
    >>> round(floating_potential(electron_temperature_ev=3.0, ion_mass=ION_MASS["xenon"]), 2)
    -15.82

    """
    if electron_temperature_ev <= 0:
        raise InvalidSpacePlasmaInputError(
            f"electron_temperature_ev must be positive, got {electron_temperature_ev!r}"
        )
    if ion_mass <= 0:
        raise InvalidSpacePlasmaInputError(f"ion_mass must be positive, got {ion_mass!r}")
    return -(electron_temperature_ev / 2) * math.log(ion_mass / (2 * math.pi * ELECTRON_MASS))
