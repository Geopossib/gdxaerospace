# Changelog

All notable changes to this project are documented in this file.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

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
