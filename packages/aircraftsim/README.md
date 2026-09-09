# aircraftsim

A simple 6-DOF aircraft flight simulator built on `flightdyn` and
`attitude3d`, with a linear aerodynamic stability-derivative model and
RK4 time integration, for the GDX Aerospace ecosystem.

```python
from aircraftsim import Aircraft6DOF

aircraft = Aircraft6DOF(mass=1200.0, inertia=(1500.0, 2000.0, 3000.0), wing_area=16.2)
state = aircraft.step(dt=0.01, controls={"elevator": 0.02, "aileron": 0.0, "rudder": 0.0, "throttle": 0.7})
```
