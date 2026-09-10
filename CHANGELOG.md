# Changelog

All notable changes to this project are documented in this file.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

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
