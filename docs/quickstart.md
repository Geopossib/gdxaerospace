# Quick start

## Standard atmosphere

```python
from aerocalc import Atmosphere

atm = Atmosphere(altitude=10_000)  # meters

print(atm.temperature)     # 223.25 K
print(atm.pressure)        # 26436.3 Pa
print(atm.density)         # 0.41271 kg/m^3
print(atm.speed_of_sound)  # 299.5 m/s
```

## Flow properties

```python
from aerocalc import Atmosphere, dynamic_pressure, mach_number, reynolds_number

atm = Atmosphere(altitude=5_000)
velocity = 220.0  # m/s

q = dynamic_pressure(density=atm.density, velocity=velocity)
mach = mach_number(velocity=velocity, speed_of_sound=atm.speed_of_sound)
re = reynolds_number(
    density=atm.density, velocity=velocity, length=2.0, temperature=atm.temperature
)

print(f"q = {q:.1f} Pa, M = {mach:.3f}, Re = {re:.3e}")
```

## Units

```python
from aerounits import Q_

cruise_alt = Q_(35_000, "ft").to("m")
cruise_speed = Q_(450, "knot").to("m/s")
```
