# gdxaerospace

The unified meta-package for the GDX Aerospace ecosystem: installing
`gdxaerospace` pulls in all 46 packages built across the project's ten
development phases (Foundation through UAV/AI/Optimization).

```python
from gdxaerospace import list_packages, package_info, phase_names

list_packages()                 # all 46 package names, sorted
list_packages(phase=6)          # ['constellationpy', 'groundtrack', 'missionpy', 'orbitpy', 'satprop', 'tletools']
package_info("orbitpy")         # PackageInfo(name='orbitpy', phase=6, phase_name='Space', description='...')
phase_names()                   # {1: 'Foundation', 2: 'Aerodynamics', ...}
```

This package deliberately does **not** re-export every symbol from
every sub-package into one flat namespace — with 46 packages, many
sharing similar names (`InvalidStressInputError`, `stall_speed`, etc.),
flattening everything would risk silent collisions. Import what you
need directly from its own package (`from orbitpy import
hohmann_transfer`, `from stresspy import von_mises_stress`, ...); use
`gdxaerospace` for dependency bundling and ecosystem discovery.

See the [root README](../../README.md) for the full package catalog,
architecture, and design principles.
