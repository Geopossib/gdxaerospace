# Changelog

All notable changes to this project are documented in this file.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

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
