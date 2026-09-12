"""The GDX Aerospace package manifest: what's in the ecosystem, and where.

This module contains no engineering logic of its own -- it is a
curated, accurate index of the other 45 packages that make up the GDX
Aerospace ecosystem, organized by the development phase each package
was built in. Installing ``gdxaerospace`` pulls in every package listed
here as a dependency; this module exists so code (and people) can
discover what's available without reading 45 separate READMEs.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PackageInfo:
    """One package's entry in the ecosystem manifest."""

    name: str
    phase: int
    phase_name: str
    description: str


_MANIFEST: dict[str, PackageInfo] = {
    # Phase 1 -- Foundation
    "aerocalc": PackageInfo(
        "aerocalc",
        1,
        "Foundation",
        "ISA atmosphere model, dynamic pressure/Mach/Reynolds number, shared exception hierarchy.",
    ),
    "aerounits": PackageInfo(
        "aerounits", 1, "Foundation", "Pint-based unit registry with aerospace unit aliases."
    ),
    # Phase 2 -- Aerodynamics
    "airfoilpy": PackageInfo(
        "airfoilpy", 2, "Aerodynamics", "NACA 4/5-digit airfoil geometry generation."
    ),
    "wingtools": PackageInfo(
        "wingtools", 2, "Aerodynamics", "Finite-wing lift slope, Oswald efficiency, induced drag."
    ),
    "dragpy": PackageInfo(
        "dragpy", 2, "Aerodynamics", "Skin-friction and component-buildup parasite drag."
    ),
    "compressibleflow": PackageInfo(
        "compressibleflow", 2, "Aerodynamics", "Isentropic flow relations, area-Mach relation."
    ),
    "shockpy": PackageInfo(
        "shockpy",
        2,
        "Aerodynamics",
        "Normal/oblique shock relations, Prandtl-Meyer expansion.",
    ),
    "boundarylayer": PackageInfo(
        "boundarylayer",
        2,
        "Aerodynamics",
        "Laminar/turbulent boundary-layer thickness and skin friction.",
    ),
    # Phase 3 -- Propulsion
    "aeroprop": PackageInfo(
        "aeroprop", 3, "Propulsion", "Airbreathing engine thrust, Isp, TSFC, Froude efficiency."
    ),
    "rocketperf": PackageInfo(
        "rocketperf", 3, "Propulsion", "Rocket exhaust velocity, Isp, c*, CF, Tsiolkovsky equation."
    ),
    "nozzleanalysis": PackageInfo(
        "nozzleanalysis", 3, "Propulsion", "Choked mass flow, nozzle area-Mach solver."
    ),
    "combustionpy": PackageInfo(
        "combustionpy", 3, "Propulsion", "Stoichiometric AFR, equivalence ratio, combustion dT."
    ),
    "turbomachpy": PackageInfo(
        "turbomachpy", 3, "Propulsion", "Compressor/turbine stage work and temperature rise."
    ),
    # Phase 4 -- Electric propulsion
    "electricprop": PackageInfo(
        "electricprop",
        4,
        "Electric Propulsion",
        "Ideal electrostatic thruster performance (Hall/ion thrusters).",
    ),
    "plasmathrust": PackageInfo(
        "plasmathrust",
        4,
        "Electric Propulsion",
        "Debye length, plasma frequency, Hall parameter, Bohm velocity.",
    ),
    "plume3d": PackageInfo(
        "plume3d", 4, "Electric Propulsion", "Thruster plume divergence correction."
    ),
    "plasmaspace": PackageInfo(
        "plasmaspace", 4, "Electric Propulsion", "Plasma floating-potential calculation."
    ),
    # Phase 5 -- Flight dynamics, guidance, navigation, control
    "attitude3d": PackageInfo(
        "attitude3d",
        5,
        "Flight Dynamics/GNC",
        "Euler/DCM/quaternion attitude representations and kinematics.",
    ),
    "flightdyn": PackageInfo(
        "flightdyn", 5, "Flight Dynamics/GNC", "Rigid-body 6-DOF equations of motion."
    ),
    "aircraftsim": PackageInfo(
        "aircraftsim",
        5,
        "Flight Dynamics/GNC",
        "13-state RK4 aircraft simulator with a linear aero model.",
    ),
    "guidancepy": PackageInfo(
        "guidancepy", 5, "Flight Dynamics/GNC", "Proportional navigation, waypoint guidance."
    ),
    "navigationpy": PackageInfo(
        "navigationpy", 5, "Flight Dynamics/GNC", "Great-circle distance/bearing, dead reckoning."
    ),
    "autopilotpy": PackageInfo(
        "autopilotpy",
        5,
        "Flight Dynamics/GNC",
        "PID control, altitude-hold/heading-hold autopilots.",
    ),
    "kalmanflight": PackageInfo(
        "kalmanflight", 5, "Flight Dynamics/GNC", "Discrete linear Kalman filter (predict/update)."
    ),
    # Phase 6 -- Space
    "orbitpy": PackageInfo(
        "orbitpy",
        6,
        "Space",
        "Two-body Keplerian mechanics, element conversions, Hohmann/bi-elliptic transfers.",
    ),
    "tletools": PackageInfo(
        "tletools", 6, "Space", "Two-Line Element checksum validation and field parsing."
    ),
    "satprop": PackageInfo(
        "satprop", 6, "Space", "SGP4 (wraps sgp4) and two-body satellite propagation."
    ),
    "groundtrack": PackageInfo(
        "groundtrack", 6, "Space", "GMST, ECI/ECEF/geodetic frames, topocentric look angles."
    ),
    "missionpy": PackageInfo("missionpy", 6, "Space", "Eclipse fraction and delta-v budgets."),
    "constellationpy": PackageInfo(
        "constellationpy", 6, "Space", "Walker constellation pattern and coverage geometry."
    ),
    # Phase 7 -- Satellite telemetry
    "sattelemetry": PackageInfo(
        "sattelemetry",
        7,
        "Satellite Telemetry",
        "CCSDS packet header, CRC-16, channel calibration, limit checking, telemetry archive.",
    ),
    # Phase 8 -- Structures and materials
    "aeromaterials": PackageInfo(
        "aeromaterials",
        8,
        "Structures/Materials",
        "Cited-source aerospace material property database.",
    ),
    "aerostruct": PackageInfo(
        "aerostruct", 8, "Structures/Materials", "Cross-section geometric properties (area, I, J)."
    ),
    "stresspy": PackageInfo(
        "stresspy",
        8,
        "Structures/Materials",
        "Axial/bending/shear/torsion stress, von Mises, principal stresses.",
    ),
    "sparcalc": PackageInfo(
        "sparcalc", 8, "Structures/Materials", "Cantilever beam deflection and shear flow."
    ),
    "bucklingpy": PackageInfo(
        "bucklingpy", 8, "Structures/Materials", "Euler column and flat-plate buckling."
    ),
    "fatiguepy": PackageInfo(
        "fatiguepy", 8, "Structures/Materials", "Basquin S-N fatigue life and Miner's rule."
    ),
    "compositepy": PackageInfo(
        "compositepy",
        8,
        "Structures/Materials",
        "Orthotropic lamina Q-matrix, transformation, failure criteria.",
    ),
    "laminatepy": PackageInfo(
        "laminatepy",
        8,
        "Structures/Materials",
        "Classical laminate theory (ABD matrix, laminate response).",
    ),
    # Phase 9 -- Thermal / CFD / data
    "aerothermal": PackageInfo(
        "aerothermal",
        9,
        "Thermal/CFD/Data",
        "Conduction/convection/radiation, thermal resistance networks, transient response.",
    ),
    "aerocfd": PackageInfo(
        "aerocfd",
        9,
        "Thermal/CFD/Data",
        "OpenFOAM case generation, execution, and post-processing.",
    ),
    "aerodata": PackageInfo(
        "aerodata",
        9,
        "Thermal/CFD/Data",
        "Flight-test/telemetry filtering, resampling, outlier detection.",
    ),
    # Phase 10 -- UAV / AI / optimization
    "uavpy": PackageInfo(
        "uavpy", 10, "UAV/AI/Optimization", "Multirotor hover power/flight time, fixed-wing sizing."
    ),
    "aerovision": PackageInfo(
        "aerovision",
        10,
        "UAV/AI/Optimization",
        "Computer-vision interfaces (Protocols) plus classical Sobel edge detection.",
    ),
    "rockettraj": PackageInfo(
        "rockettraj",
        10,
        "UAV/AI/Optimization",
        "Vertical rocket trajectory simulation (ascent, coast, apogee).",
    ),
    "aeroopt": PackageInfo(
        "aeroopt",
        10,
        "UAV/AI/Optimization",
        "SciPy optimization wrapper and worked design-optimization examples.",
    ),
}


def list_packages(*, phase: int | None = None) -> list[str]:
    """List package names in the ecosystem manifest, sorted alphabetically.

    Parameters
    ----------
    phase:
        If given, only list packages from this development phase
        (1-10). If omitted, lists all packages.

    Returns
    -------
    list[str]

    Example
    -------
    >>> "aerocalc" in list_packages()
    True
    >>> list_packages(phase=1)
    ['aerocalc', 'aerounits']

    """
    entries = (
        _MANIFEST.values() if phase is None else (p for p in _MANIFEST.values() if p.phase == phase)
    )
    return sorted(p.name for p in entries)


def package_info(name: str) -> PackageInfo:
    """Look up a package's manifest entry by name.

    Parameters
    ----------
    name:
        Package name (e.g. ``"orbitpy"``).

    Returns
    -------
    PackageInfo

    Raises
    ------
    KeyError
        If ``name`` is not in the manifest.

    Example
    -------
    >>> info = package_info("orbitpy")
    >>> info.phase
    6

    """
    return _MANIFEST[name]


def phase_names() -> dict[int, str]:
    """Return a mapping of phase number to phase name.

    Example:
    -------
    >>> phase_names()[1]
    'Foundation'

    """
    return {p.phase: p.phase_name for p in _MANIFEST.values()}
