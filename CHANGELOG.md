# Changelog

All notable changes to this project are documented in this file.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [0.9.0] — Phase 9: Thermal Analysis, CFD Automation, and Flight Data

### Added
- `aerothermal`: conduction (Fourier), convection (Newton's law of
  cooling), and radiation (Stefan-Boltzmann) heat transfer; series/
  parallel thermal resistance networks; lumped-capacitance transient
  response; and a spacecraft radiative-equilibrium temperature estimate.
- `aerocfd`: a Python automation layer around OpenFOAM -- case-file
  generation (correct FoamFile dictionary syntax for controlDict,
  transportProperties, turbulenceProperties, and the U/p fields),
  availability detection, and forceCoeffs post-processing. Never
  assumes OpenFOAM is installed: detects its absence and raises a
  clear error with install instructions rather than a bare subprocess
  failure, matching the project's original design requirement.
- `aerodata`: pandas-based flight-test/telemetry time-series analysis
  -- moving-average smoothing, linear resampling to a uniform time
  base, descriptive statistics, and z-score outlier detection.
- Thermal/CFD/data theory docs, API reference pages for all three
  packages, and an example script covering a spacecraft thermal
  estimate, a full OpenFOAM case-generation-and-run-attempt workflow,
  and flight-data outlier detection (including a worked demonstration
  of why detrending before z-score screening matters -- the first
  version of the demo's undetrended series masked its own injected
  glitch, exactly the documented z-score limitation, and detrending
  fixed it).
- 717 tests + 180 doctests passing, ruff clean across all 41 packages.

## [0.8.0] — Phase 8: Structures and Materials

### Added
- `aeromaterials`: a 5-material property database (Al 7075-T6, Al
  2024-T3, Ti-6Al-4V, AISI 4340, ASTM A36 steel), every value cited to
  MMPDS-01/ASM or the governing specification, with explicit caveats
  where strength is too heat-treatment-dependent to responsibly quote.
- `aerostruct`: cross-section geometric properties (rectangle, solid/
  hollow circle, I-beam via parallel-axis composite decomposition).
- `stresspy`: axial, bending, transverse-shear, and torsional stress;
  von Mises equivalent stress; principal stresses via Mohr's circle.
  Validated against real invariants (trace preservation, pure-shear
  von Mises = sqrt(3)*tau).
- `sparcalc`: cantilever beam tip deflection (point and distributed
  load) and thin-wall shear flow.
- `bucklingpy`: Euler column buckling for all four standard end
  conditions (with the classic 4x/16x stiffness-ratio comparisons
  verified directly) and flat-plate buckling.
- `fatiguepy`: Basquin power-law S-N fatigue life and its inverse, and
  Palmgren-Miner cumulative damage summation.
- `compositepy`: orthotropic lamina reduced-stiffness (Q) matrix and
  axis transformation (Q-bar), validated against the canonical
  T300/5208 graphite-epoxy properties and self-consistency checks
  (theta=0 recovers material axes, theta=90 swaps Q11/Q22, theta=45
  gives Q11=Q22); max-stress and Tsai-Hill failure criteria.
- `laminatepy`: Classical Laminate Theory ABD matrix assembly and
  laminate mid-plane strain/curvature response to applied loads,
  validated against the core CLT identity that a mid-plane-symmetric
  laminate has exactly zero coupling stiffness (B = 0).
- Structures/materials theory docs, API reference pages for all eight
  packages, and an example script sizing a metallic I-beam spar
  (bending, deflection, buckling, fatigue) and analyzing a symmetric
  composite laminate panel.

## [0.7.0] — Phase 7: Satellite Telemetry

### Added
- `sattelemetry`: a full CCSDS-style telemetry decode/validate/
  calibrate/archive pipeline --
  - CCSDS Space Packet primary header pack/unpack (CCSDS 133.0-B-2),
    round-trip verified across all fields at non-trivial values.
  - CRC-16/CCITT-FALSE checksum, anchored to the standard published
    check value (0x29B1 for "123456789").
  - Polynomial raw-to-engineering-unit channel calibration.
  - A packet decoder tying header + CRC + channels together into named,
    calibrated values from raw bytes.
  - Red/yellow limit checking, the standard first-line spacecraft
    operations anomaly-detection method.
  - An in-memory, queryable telemetry archive with z-score statistical
    outlier detection.
- Satellite telemetry theory/architecture docs, an API reference page,
  and an example script simulating a telemetry pass with an injected
  anomaly, caught independently by both the limit checker and the
  statistical outlier detector.

### Fixed (during development, before release)
- The packet decoder initially computed CRC over the data field when
  building a packet but verified it over header+data when decoding --
  a scope mismatch that made every valid packet fail verification.
  Fixed by settling on and documenting one explicit convention (CRC
  covers the data field only, matching the ECSS/PUS standard).
- The archive's first outlier-detection doctest example didn't actually
  trigger detection: a single extreme outlier in a short series
  inflates its own standard deviation enough to mask itself (a known
  z-score limitation). Fixed with a longer, more representative example
  series and documented the limitation explicitly.

## [0.6.0] — Phase 6: Space

### Added
- `orbitpy`: two-body Keplerian mechanics — orbital period, circular/
  escape velocity, vis-viva equation, Kepler's equation solver, full
  Keplerian-element/Cartesian-state-vector conversion (Vallado's
  algorithms, round-trip verified across 6 orbit types), and Hohmann/
  bi-elliptic transfers with plane-change delta-v. Confirms the
  bi-elliptic-vs-Hohmann crossover at the ~11.94 radius-ratio threshold.
- `tletools`: Two-Line Element checksum computation/validation and full
  fixed-column field parsing, validated against the canonical Vallado
  SGP4 verification TLE (ISS, epoch 2008) used across the field.
- `satprop`: a thin wrapper around the MIT-licensed `sgp4` library for
  TLE-based propagation (GDX Aerospace does not reimplement SGP4 --
  see the project's "wrap, don't reinvent" stance in the docs), plus
  analytic two-body propagation for non-TLE/hypothetical orbits built
  on `orbitpy`.
- `groundtrack`: Julian date, Greenwich Mean Sidereal Time, ECI-ECEF
  rotation, WGS84 geodetic/ECEF conversion (round-trip verified
  pole-to-equator), and topocentric azimuth/elevation/range look angles.
- `missionpy`: cylindrical-shadow eclipse fraction/duration (derived
  from first principles and cross-checked against the general
  beta-angle formula via a trig identity) and an itemized delta-v
  budget with margin.
- `constellationpy`: Walker Delta ("i:t/p/f") constellation pattern
  generation and single-satellite ground coverage geometry, validated
  against a GPS-like 24-satellite/6-plane pattern.
- Orbital mechanics theory docs, API reference pages for all six
  packages, and an example script tying TLE propagation, ground
  tracking, mission delta-v budgeting, and constellation geometry
  together (its GPS-like coverage-angle output matches real GPS
  constellation design figures).

## [0.5.0] — Phase 5: Flight Dynamics, Guidance, Navigation, and Control

### Added
- `attitude3d`: Euler angle (3-2-1 sequence), DCM, and quaternion
  conversions, quaternion kinematics, and a Shepperd-algorithm
  DCM-to-quaternion solver that stays numerically robust near 180-degree
  rotations (unlike a naive trace-only method).
- `flightdyn`: rigid-body 6-DOF equations of motion — translational
  acceleration (with the rotating-frame Coriolis-like term), Euler's
  rotational equations (general inertia matrix or diagonal shortcut),
  body-frame gravity, and position kinematics.
- `aircraftsim`: `Aircraft6DOF`, an RK4-integrated 6-DOF simulator
  combining `flightdyn`/`attitude3d` with a generic linear
  stability-derivative aerodynamic model (`LinearAeroModel`), matching
  the API shape from the original project brief. Illustrative default
  coefficients only — not validated flight data for any real aircraft.
- `guidancepy`: proportional navigation (line-of-sight rate, closing
  velocity, PN acceleration command) per Zarchan, plus waypoint
  bearing/distance and signed cross-track error.
- `navigationpy`: great-circle distance and initial bearing (haversine),
  and dead-reckoning position propagation (direct geodesic problem on a
  sphere), validated against the well-known JFK-LHR great-circle distance.
- `autopilotpy`: a discrete PID controller with conditional-integration
  anti-windup, plus `AltitudeHoldAutopilot`/`HeadingHoldAutopilot`
  wrappers (the latter with correct 0/360-degree heading wraparound).
- `kalmanflight`: a discrete linear Kalman filter with Joseph-form
  covariance update, validated against a hand-computable scalar case and
  a classic constant-velocity tracking scenario.
- Flight dynamics/GNC theory docs and API reference pages for all seven
  packages; an example script flying a closed-loop altitude-hold climb
  and demonstrating guidance/navigation/estimation together.

### Fixed
- `AltitudeHoldAutopilot` had an inverted sign convention relative to
  `LinearAeroModel`'s `Cm_elevator` (correctly negative per the standard
  aerospace convention), which caused closed-loop divergence into a dive.
  Corrected the error sign so climbing now correctly commands negative
  (nose-up) elevator.

## [0.4.0] — Phase 4: Electric Propulsion

### Added
- `plasmathrust`: fundamental plasma parameters (Debye length, plasma
  frequency, electron/ion cyclotron frequency, Larmor radius, Hall
  parameter, Bohm velocity) and a shared physical-constants module with
  common electric-propulsion propellant ion masses (xenon, krypton,
  argon, hydrogen).
- `electricprop`: ideal electrostatic exhaust velocity, thrust from beam
  current, specific impulse, and total thrust efficiency (Goebel & Katz),
  plus `HallThruster`/`IonThruster` convenience classes.
- `plume3d`: a simplified single-angle plume-divergence correction for
  thrust and specific impulse, explicitly documented as an optimistic
  upper bound relative to a full angular current-density integral.
- `plasmaspace`: floating potential of an isolated conductor in a
  Maxwellian plasma, derived from first principles (electron thermal
  flux vs. Bohm ion flux current balance) and validated against the
  well-known reference coefficient for argon (~4.68 * Te[eV]).
- Electric-propulsion/plasma theory docs and API reference pages for all
  four packages.
- Example script comparing Hall vs. ion thruster performance, checking
  Hall-thruster electron magnetization, and estimating spacecraft
  floating potential.

## [0.3.0] — Phase 3: Propulsion

### Added
- `aeroprop`: uninstalled air-breathing thrust equation, specific impulse,
  thrust-specific fuel consumption, and propulsive (Froude) efficiency,
  per Mattingly's *Elements of Gas Turbine Propulsion*.
- `rocketperf`: effective exhaust velocity, specific impulse,
  characteristic velocity (c*), thrust coefficient (CF), and the ideal
  (Tsiolkovsky) rocket equation with its inverse, per Sutton & Biblarz's
  *Rocket Propulsion Elements*.
- `nozzleanalysis`: choked mass flow through a converging-diverging
  nozzle, a bisection solver inverting the isentropic area-Mach relation
  for exit Mach number, and isentropic exit temperature/velocity.
- `combustionpy`: stoichiometric air-fuel ratio for `CxHyOz` hydrocarbon
  fuels (validated against Turns's published reference values), the
  equivalence ratio, and a clearly-labeled simplified constant-cp
  adiabatic temperature-rise estimate for conceptual-design screening.
- `turbomachpy`: compressor and turbine stage actual temperature
  change and specific work from pressure ratio and isentropic efficiency,
  per Mattingly and Cohen/Rogers/Saravanamuttoo's *Gas Turbine Theory*.
- Propulsion theory docs and API reference pages for all five packages.
- Example script analyzing a liquid rocket engine and a simple turbojet
  Brayton cycle end-to-end.

## [0.2.0] — Phase 2: Aerodynamics

### Added
- `airfoilpy`: NACA 4-digit and standard NACA 5-digit airfoil geometry
  (camber line, thickness distribution, surface coordinates), validated
  against Abbott & Von Doenhoff's published characteristics.
- `wingtools`: finite-wing lift-curve-slope correction (Prandtl and
  Helmbold models), Oswald efficiency estimate (Raymer correlation), and
  induced-drag coefficient.
- `dragpy`: laminar (Blasius) and turbulent (Prandtl 1/5-power,
  Schlichting) flat-plate skin-friction coefficients, plus a
  component-buildup parasitic drag model.
- `compressibleflow`: isentropic stagnation-property ratios and the
  area-Mach relation for a calorically perfect gas, validated exactly
  against Anderson's Appendix A tables.
- `shockpy`: normal shock relations, an oblique-shock (theta-beta-M)
  bisection solver with weak/strong solution selection and detached-shock
  detection, and the Prandtl-Meyer expansion function with its inverse —
  all validated against Anderson's Appendix B/C tables.
- `boundarylayer`: Blasius laminar and 1/7-power-law turbulent
  boundary-layer thickness and local skin-friction coefficients.
- Theory docs for airfoils/finite wings and compressible flow/shocks;
  API reference pages for all six new packages.

## [0.1.0] — Phase 1: Foundation

### Added
- Monorepo architecture (`packages/`, `docs/`, `examples/`, `tests/`,
  `benchmarks/`, `notebooks/`, `scripts/`).
- `aerounits`: SI/Imperial/US-customary unit system built on Pint, with an
  aerospace-relevant default unit registry (knots, feet, slugs, etc.).
- `aerocalc`: core numerical utilities, shared exception hierarchy, and the
  ISA (International Standard Atmosphere) model exposed via the
  `Atmosphere` class, plus Mach number, Reynolds number, and dynamic
  pressure helpers.
- Pytest-based test suite validated against ICAO Doc 7488 / U.S. Standard
  Atmosphere 1976 reference tables.
- Sphinx + MyST documentation scaffold.
- GitHub Actions CI: `tests.yml`, `lint.yml`, `docs.yml`.
- Root `README.md`, `LICENSE` (MIT), `CONTRIBUTING.md`,
  `CODE_OF_CONDUCT.md`, `SECURITY.md`.
