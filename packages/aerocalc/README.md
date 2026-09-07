# aerocalc

Core atmospheric and flow-property calculations for the GDX Aerospace
ecosystem: the International Standard Atmosphere (ISA), dynamic pressure,
Mach number, Reynolds number, and the shared exception hierarchy used
across the ecosystem.

```python
from aerocalc import Atmosphere, dynamic_pressure, mach_number, reynolds_number

atm = Atmosphere(altitude=10_000)  # meters
print(atm.temperature, atm.pressure, atm.density, atm.speed_of_sound)

q = dynamic_pressure(density=atm.density, velocity=250)
M = mach_number(velocity=250, speed_of_sound=atm.speed_of_sound)
Re = reynolds_number(density=atm.density, velocity=250, length=2.5, temperature=atm.temperature)
```

## Model coverage (Phase 1)

- `Atmosphere`: 1976 U.S. Standard Atmosphere / ICAO Doc 7488, all seven
  layers, 0–86,000 m.
- `dynamic_pressure`, `mach_number`, `reynolds_number`, `sutherland_viscosity`.
- `aerocalc.exceptions`: the shared `GDXAerospaceError` hierarchy other GDX
  Aerospace packages build on.

Aerodynamic coefficients, airfoil geometry, compressible-flow relations,
and boundary-layer models land in Phase 2 (`airfoilpy`, `wingtools`,
`dragpy`, `compressibleflow`, `shockpy`, `boundarylayer`).
