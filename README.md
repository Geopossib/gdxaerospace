# GDX Aerospace

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Tests](https://github.com/Geopossib/gdxaerospace/actions/workflows/tests.yml/badge.svg)](https://github.com/Geopossib/gdxaerospace/actions/workflows/tests.yml)
[![Lint](https://github.com/Geopossib/gdxaerospace/actions/workflows/lint.yml/badge.svg)](https://github.com/Geopossib/gdxaerospace/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-alpha-orange)]()

**GDX Aerospace** is a professional, open-source Python ecosystem for aerospace
engineering — aerodynamics, propulsion, electric propulsion, flight dynamics,
orbital mechanics, satellite telemetry, structures, thermal analysis, CFD
automation, UAV design, and more.

It is built for aerospace engineering students, researchers, universities,
UAV developers, satellite engineers, and aerospace startups who need real,
citable, tested engineering calculations — not toy demonstrations.

> **Status:** Phase 1 (Foundation) and Phase 2 (Aerodynamics) are complete.
> See [Roadmap](#roadmap).

## Design principles

- Every calculation states its governing equations, assumptions, and valid
  input ranges in its docstring.
- All internal computation uses SI units. Unit conversion is explicit and
  handled by `aerounits` (built on [Pint](https://pint.readthedocs.io/)).
- Where a phenomenon has multiple models (e.g. standard vs. hot-day
  atmosphere), the model is a named, explicit parameter — never an implicit
  default that changes behavior silently.
- Invalid or out-of-range inputs raise a specific, descriptive exception —
  results are never silently wrong.
- Every public function has an automated test that checks numerical
  correctness against a textbook or standard reference value, not just that
  the function runs.

## Architecture

This is a monorepo of independently versioned/installable packages under
`packages/`, plus a unifying `gdxaerospace` meta-package (added in Phase 11).

```
gdxaerospace/
├── packages/
│   ├── aerounits/     # SI/Imperial unit system built on Pint
│   ├── aerocalc/      # Atmosphere, Mach/Reynolds/dynamic pressure, core numerics
│   ├── airfoilpy/     # NACA 4/5-digit airfoil geometry
│   ├── wingtools/     # Finite-wing lift-curve-slope & induced drag corrections
│   ├── dragpy/        # Skin-friction & parasitic drag build-up
│   ├── compressibleflow/  # Isentropic flow relations
│   ├── shockpy/       # Normal/oblique shocks, Prandtl-Meyer expansion
│   ├── boundarylayer/ # Laminar/turbulent boundary-layer relations
│   └── ...            # more packages land in later phases
├── docs/
├── examples/
├── tests/
├── benchmarks/
├── notebooks/
├── scripts/
└── .github/workflows/
```

## Installation (development)

This project uses [uv](https://docs.astral.sh/uv/) for workspace management.

```bash
git clone https://github.com/Geopossib/gdxaerospace.git
cd gdxaerospace
uv sync
```

Or, to install a single package with pip during development:

```bash
pip install -e packages/aerounits
pip install -e packages/aerocalc
```

## Quick start

```python
from aerocalc import Atmosphere

atm = Atmosphere(altitude=10_000)  # meters, ISA standard atmosphere

print(atm.temperature)   # Kelvin
print(atm.pressure)      # Pascal
print(atm.density)       # kg/m^3
print(atm.speed_of_sound)  # m/s
```

```python
from aerounits import Q_

speed = Q_(250, "knot").to("m/s")
print(speed)
```

```python
from airfoilpy import naca4_coordinates
from shockpy import normal_shock, oblique_shock
import math

coords = naca4_coordinates("2412", n_points=200)

shock = normal_shock(mach1=2.0)
print(shock.mach_downstream, shock.pressure_ratio)  # 0.577, 4.5

oblique = oblique_shock(mach1=2.0, deflection=math.radians(10.0))
print(math.degrees(oblique.shock_angle))  # ~39.3 deg
```

## Testing

```bash
uv run pytest
```

Tests validate numerical results against ISA tables (ICAO Doc 7488 / U.S.
Standard Atmosphere 1976) and other published reference values — see each
package's `tests/` directory and docstrings for the specific source cited.

## Roadmap

- [x] **Phase 1 — Foundation**: repo architecture, `aerounits`, `aerocalc`
      core, exceptions, test/doc framework, CI/CD
- [x] **Phase 2 — Aerodynamics**: `airfoilpy`, `wingtools`, `dragpy`,
      `compressibleflow`, `shockpy`, `boundarylayer`
- [ ] **Phase 3 — Propulsion**: `aeroprop`, `rocketperf`, `nozzleanalysis`,
      `combustionpy`, `turbomachpy`
- [ ] **Phase 4 — Electric propulsion**: `electricprop`, `plasmathrust`,
      `plume3d`, `plasmaspace`
- [ ] **Phase 5 — Flight dynamics**: `flightdyn`, `aircraftsim`,
      `attitude3d`, `guidancepy`, `navigationpy`, `autopilotpy`,
      `kalmanflight`
- [ ] **Phase 6 — Space**: `orbitpy`, `satprop`, `tletools`, `groundtrack`,
      `missionpy`, `constellationpy`
- [ ] **Phase 7 — Satellite telemetry**: `sattelemetry`
- [ ] **Phase 8 — Structures & materials**: `aerostruct`, `sparcalc`,
      `stresspy`, `fatiguepy`, `compositepy`, `laminatepy`, `bucklingpy`,
      `aeromaterials`
- [ ] **Phase 9 — Thermal / CFD / data**: `aerothermal`, `aerocfd`,
      `aerodata`
- [ ] **Phase 10 — UAV / AI / optimization**: `uavpy`, `aerovision`,
      `rockettraj`, `aeroopt`
- [ ] **Phase 11 — Unified ecosystem**: `gdxaerospace` meta-package

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

GDX Aerospace is an engineering research and education library. Simplified
models and assumptions are clearly labeled in each function's docstring.
**No result from this library should be treated as certified flight-critical
engineering analysis without independent professional verification.**
