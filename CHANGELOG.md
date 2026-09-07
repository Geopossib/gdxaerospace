# Changelog

All notable changes to this project are documented in this file.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

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
