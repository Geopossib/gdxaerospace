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

> **Status:** Phases 1-8 (Foundation, Aerodynamics, Propulsion, Electric
> Propulsion, Flight Dynamics/GNC, Space, Satellite Telemetry, and
> Structures/Materials) are complete. See [Roadmap](#roadmap).

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
│   ├── aeroprop/      # General air-breathing thrust, Isp, TSFC, propulsive efficiency
│   ├── rocketperf/    # Rocket Isp, c*, CF, ideal rocket equation
│   ├── nozzleanalysis/ # Isentropic nozzle flow (choked mass flow, exit conditions)
│   ├── combustionpy/  # Combustion stoichiometry & simplified temperature rise
│   ├── turbomachpy/   # Compressor/turbine stage temperature change & work
│   ├── plasmathrust/  # Fundamental plasma parameters (Debye length, cyclotron motion)
│   ├── electricprop/  # Ion/Hall thruster exhaust velocity, thrust, Isp, efficiency
│   ├── plume3d/       # Simplified plume-divergence thrust/Isp loss
│   ├── plasmaspace/   # Spacecraft floating potential (plasma current balance)
│   ├── attitude3d/    # Euler/DCM/quaternion attitude representation & kinematics
│   ├── flightdyn/     # Rigid-body 6-DOF equations of motion
│   ├── aircraftsim/   # Aircraft6DOF: RK4-integrated flight simulator
│   ├── guidancepy/    # Proportional navigation & waypoint/cross-track guidance
│   ├── navigationpy/  # Great-circle distance/bearing & dead reckoning
│   ├── autopilotpy/   # PID controller (anti-windup) & altitude/heading hold
│   ├── kalmanflight/  # Discrete linear Kalman filter (predict/update)
│   ├── orbitpy/       # Two-body Keplerian mechanics, transfers, element conversions
│   ├── tletools/      # TLE checksum validation & field parsing
│   ├── satprop/       # SGP4 (wraps sgp4) and two-body satellite propagation
│   ├── groundtrack/   # GMST, ECI/ECEF/geodetic frames, topocentric look angles
│   ├── missionpy/     # Eclipse fraction & delta-v budgets
│   ├── constellationpy/ # Walker constellation pattern & coverage geometry
│   ├── sattelemetry/  # CCSDS packet header, CRC-16, calibration, limits, archive
│   ├── aeromaterials/ # Cited-source aerospace material property database
│   ├── aerostruct/    # Cross-section geometric properties (area, I, J)
│   ├── stresspy/      # Axial/bending/shear/torsion stress, von Mises, principal stresses
│   ├── sparcalc/      # Cantilever beam deflection & shear flow
│   ├── bucklingpy/    # Euler column & flat-plate buckling
│   ├── fatiguepy/     # Basquin S-N fatigue life & Miner's rule
│   ├── compositepy/   # Orthotropic lamina Q-matrix, transformation, failure criteria
│   ├── laminatepy/    # Classical laminate theory (ABD matrix, laminate response)
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

```python
from electricprop import HallThruster

thruster = HallThruster(voltage=300.0, current=4.5, mass_flow=5e-6)
print(thruster.thrust(), thruster.specific_impulse(), thruster.efficiency())
```

```python
from aircraftsim import Aircraft6DOF
from autopilotpy import AltitudeHoldAutopilot

aircraft = Aircraft6DOF(mass=1200.0, inertia=(1500.0, 2000.0, 3000.0), wing_area=16.2)
altitude_hold = AltitudeHoldAutopilot()

state = aircraft.state_snapshot()
elevator = altitude_hold.command(state["altitude"], target_altitude=1050.0, dt=0.05)
state = aircraft.step(dt=0.05, controls={"elevator": elevator, "throttle": 0.7})
```

```python
import datetime as dt
from satprop import propagate_tle
from orbitpy import hohmann_transfer

line1 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
line2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
position, velocity = propagate_tle(line1, line2, dt.datetime(2008, 9, 20, 12, 25, 40))

transfer = hohmann_transfer(r1=6_678_000.0, r2=42_164_000.0)  # LEO -> GEO
print(transfer.total_delta_v)  # ~3893 m/s
```

```python
import struct
from sattelemetry import PacketLayout, TelemetryChannel, TelemetryDecoder, append_crc, pack_primary_header

layout = PacketLayout(
    name="housekeeping", apid=100,
    channels=(TelemetryChannel("battery_voltage", 0, "u16", "V", (0.0, 5.0 / 4095.0)),),
)
data = append_crc(struct.pack(">H", 3200))
packet = pack_primary_header(apid=100, data_length=len(data)) + data
decoded = TelemetryDecoder([layout]).decode(packet)
print(decoded.values["battery_voltage"])  # ~3.907 V
```

```python
from aeromaterials import get_material
from aerostruct import i_beam_properties
from stresspy import bending_stress

material = get_material("Al7075-T6")
section = i_beam_properties(flange_width=0.06, flange_thickness=0.008, web_height=0.08, web_thickness=0.005)
stress = bending_stress(moment=6000.0, distance_from_neutral_axis=0.048, moment_of_inertia=section.ixx)
print(stress / 1e6, "MPa vs yield", material.yield_strength / 1e6, "MPa")
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
- [x] **Phase 3 — Propulsion**: `aeroprop`, `rocketperf`, `nozzleanalysis`,
      `combustionpy`, `turbomachpy`
- [x] **Phase 4 — Electric propulsion**: `electricprop`, `plasmathrust`,
      `plume3d`, `plasmaspace`
- [x] **Phase 5 — Flight dynamics**: `flightdyn`, `aircraftsim`,
      `attitude3d`, `guidancepy`, `navigationpy`, `autopilotpy`,
      `kalmanflight`
- [x] **Phase 6 — Space**: `orbitpy`, `satprop`, `tletools`, `groundtrack`,
      `missionpy`, `constellationpy`
- [x] **Phase 7 — Satellite telemetry**: `sattelemetry`
- [x] **Phase 8 — Structures & materials**: `aerostruct`, `sparcalc`,
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
