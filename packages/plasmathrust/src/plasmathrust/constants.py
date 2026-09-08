"""Fundamental physical constants and common ion masses for plasma calculations.

Reference
---------
- CODATA 2018 recommended values (elementary charge, electron mass,
  Boltzmann constant), as tabulated in NIST's Fundamental Physical
  Constants.
- Ion masses computed from standard atomic weights (IUPAC 2021) times the
  unified atomic mass unit.
"""

from __future__ import annotations

#: Elementary charge, C.
ELEMENTARY_CHARGE = 1.602176634e-19
#: Electron rest mass, kg.
ELECTRON_MASS = 9.1093837015e-31
#: Boltzmann constant, J/K.
BOLTZMANN_CONSTANT = 1.380649e-23
#: Unified atomic mass unit, kg.
ATOMIC_MASS_UNIT = 1.66053906660e-27
#: Vacuum permittivity, F/m.
VACUUM_PERMITTIVITY = 8.8541878128e-12

#: Common electric-propulsion propellant ion masses, kg (standard atomic weight * amu).
ION_MASS = {
    "xenon": 131.293 * ATOMIC_MASS_UNIT,
    "krypton": 83.798 * ATOMIC_MASS_UNIT,
    "argon": 39.948 * ATOMIC_MASS_UNIT,
    "hydrogen": 1.008 * ATOMIC_MASS_UNIT,
}
